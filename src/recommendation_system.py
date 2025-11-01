"""
Sistema de Recomanacions d'Animes
Motor principal amb collaborative filtering i Pearson correlation
"""

from src.models.anime import Anime
from src.models.user import User
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path
from datetime import datetime


class RecommendationSystem:

    def __init__(self, anime_csv_path='data/anime.csv', rating_csv_path='data/cleaned_data.csv', model_dir='model'):
        """
        Inicialitza el sistema de recomanacions carregant el model més recent
        """
        self.animes_dict = {}
        self.users_dict = {}
        self.ratings_df = None
        self.userRatings_pivot = None
        self.corrMatrix = None
        self.animeStats = None
        self.animePopularity = None  # Nova: per guardar popularitat
        self.animeAvgRating = None   # Nova: per guardar rating mitjà
        self.model_dir = Path(__file__).resolve().parent.parent / model_dir
        self.anime_csv_path = Path(anime_csv_path)
        self.rating_csv_path = Path(rating_csv_path)
        
        # Info del model carregat
        self.current_model_version = None
        self.model_load_time = None
        self.data_files_hash = None  # Per detectar canvis
        
        # Crear directori model si no existeix
        self.model_dir.mkdir(exist_ok=True)
        
        # Intentar carregar model entrenat
        if not self._load_latest_model():
            print("\n" + "="*70)
            print("⚠️  CAP MODEL ENTRENAT TROBAT")
            print("="*70)
            print("\nEl directori 'model/' està buit o no conté models vàlids.")
            print("\n🔧 Per generar el model, executa:")
            print("   python scripts/train_model.py")
            print("\nO des de la carpeta arrel:")
            print("   ./scripts/train_auto.sh")
            print("="*70)
            raise FileNotFoundError(
                "No s'ha trobat cap model entrenat. "
                "Executa train_model() abans d'usar el sistema."
            )
    
    def get_data_files_hash(self):
        """
        Calcula un hash dels fitxers de dades per detectar canvis
        Utilitza el timestamp de modificació dels fitxers CSV
        """
        try:
            anime_mtime = self.anime_csv_path.stat().st_mtime
            rating_mtime = self.rating_csv_path.stat().st_mtime
            return f"{anime_mtime}_{rating_mtime}"
        except Exception:
            return None
    
    def has_data_changed(self):
        """
        Comprova si els fitxers de dades han canviat des de l'últim entrenament
        
        Returns:
            bool: True si les dades han canviat, False altrament
        """
        current_hash = self.get_data_files_hash()
        if current_hash is None or self.data_files_hash is None:
            return False
        return current_hash != self.data_files_hash
    
    def _get_latest_version(self):
        """
        Troba l'última versió del model disponible
        
        Returns:
            int: Número de la versió més recent (0 si no n'hi ha cap)
        """
        if not self.model_dir.exists():
            return 0
        
        versions = []
        for file in self.model_dir.glob('corr_matrix_v*.pkl'):
            try:
                version_str = file.stem.split('_v')[1]
                versions.append(int(version_str))
            except (IndexError, ValueError):
                continue
        
        return max(versions) if versions else 0
    
    def _get_next_version(self):
        """
        Retorna el següent número de versió disponible
        """
        return self._get_latest_version() + 1
    
    def _load_latest_model(self):
        """
        Carrega l'última versió del model entrenat
        
        Returns:
            bool: True si s'ha carregat correctament, False altrament
        """
        latest_version = self._get_latest_version()
        
        if latest_version == 0:
            return False
        
        model_path = self.model_dir / f'corr_matrix_v{latest_version}.pkl'
        
        print(f"\n📦 Carregant model v{latest_version} des de {model_path}...")
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Carregar les dades guardades
            self.animes_dict = model_data['animes_dict']
            self.users_dict = model_data['users_dict']
            self.ratings_df = model_data['ratings_df']
            self.userRatings_pivot = model_data['userRatings_pivot']
            self.corrMatrix = model_data['corrMatrix']
            self.animeStats = model_data['animeStats']
            
            # Carregar estadístiques addicionals si existeixen
            self.animePopularity = model_data.get('animePopularity')
            self.animeAvgRating = model_data.get('animeAvgRating')
            
            # Si no existeixen, calcular-les
            if self.animePopularity is None:
                self._calculate_anime_stats()
            
            # Guardar info del model
            self.current_model_version = latest_version
            self.model_load_time = datetime.now()
            self.data_files_hash = model_data.get('data_files_hash')
            
            print(f"✅ Model v{latest_version} carregat correctament!")
            print(f"   - {len(self.animes_dict)} animes")
            print(f"   - {len(self.users_dict)} usuaris")
            print(f"   - Matriu de correlacions: {self.corrMatrix.shape}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error carregant el model: {str(e)}")
            return False
    
    def _calculate_anime_stats(self):
        """
        Calcula estadístiques addicionals dels animes
        """
        if self.ratings_df is not None:
            # Popularitat (nombre de valoracions)
            self.animePopularity = self.ratings_df.groupby('name')['rating'].count()
            
            # Rating mitjà
            self.animeAvgRating = self.ratings_df.groupby('name')['rating'].mean()
    
    def reload_model(self):
        """
        Recarrega el model més recent disponible
        Útil quan s'ha entrenat un model nou en background
        
        Returns:
            bool: True si s'ha recarregat correctament
        """
        print("\n🔄 Recarregant model més recent...")
        return self._load_latest_model()
    
    def train_model(self, save=True):
        """
        Entrena el model calculant la matriu de correlacions
        Aquest procés pot trigar uns minuts amb datasets grans
        
        Args:
            save (bool): Si True, guarda el model en un fitxer PKL versionat
        """
        print("\n" + "="*70)
        print("🚀 INICIANT ENTRENAMENT DEL MODEL")
        print("="*70)
        
        # Carregar dades dels CSV
        self._load_data_for_training(self.anime_csv_path, self.rating_csv_path)
        
        if save:
            # Guardar el model amb la següent versió
            next_version = self._get_next_version()
            model_path = self.model_dir / f'corr_matrix_v{next_version}.pkl'
            
            print(f"\n💾 Guardant model v{next_version} a {model_path}...")
            
            # Calcular hash dels fitxers de dades
            data_hash = self.get_data_files_hash()
            
            model_data = {
                'animes_dict': self.animes_dict,
                'users_dict': self.users_dict,
                'ratings_df': self.ratings_df,
                'userRatings_pivot': self.userRatings_pivot,
                'corrMatrix': self.corrMatrix,
                'animeStats': self.animeStats,
                'animePopularity': self.animePopularity,
                'animeAvgRating': self.animeAvgRating,
                'version': next_version,
                'anime_csv_path': str(self.anime_csv_path),
                'rating_csv_path': str(self.rating_csv_path),
                'data_files_hash': data_hash,
                'created_at': datetime.now().isoformat()
            }
            
            try:
                with open(model_path, 'wb') as f:
                    pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                print(f"✅ Model v{next_version} guardat correctament!")
                print(f"   Mida del fitxer: {model_path.stat().st_size / (1024*1024):.1f} MB")
                
                # Actualitzar info del model actual
                self.current_model_version = next_version
                self.model_load_time = datetime.now()
                self.data_files_hash = data_hash
                
            except Exception as e:
                print(f"❌ Error guardant el model: {str(e)}")
                raise
        
        print("="*70)
        print("✅ ENTRENAMENT COMPLETAT!")
        print("="*70)
    
    def _load_data_for_training(self, anime_csv_path, rating_csv_path):
        """
        Carrega i processa les dades dels CSV per entrenar el model
        """
        print("\n📂 Carregant dades dels CSV...")
        
        # Llegir anime.csv amb encoding UTF-8
        a_cols = ['anime_id', 'name', 'genre', 'members']
        animes_df = pd.read_csv(
            anime_csv_path, 
            sep=',', 
            usecols=a_cols, 
            encoding="utf-8",  # Canviat a UTF-8
            on_bad_lines='skip'  # Saltar línies problemàtiques
        )
        
        # Llegir rating CSV amb encoding UTF-8
        ratings_df = pd.read_csv(
            rating_csv_path, 
            sep=',', 
            encoding="utf-8",  # Canviat a UTF-8
            on_bad_lines='skip'
        )
        
        # Merge de les dades
        self.ratings_df = pd.merge(animes_df, ratings_df)
        
        print(f"   ✓ Dades carregades: {len(self.ratings_df)} valoracions")
        
        # Crear objectes Anime
        print(f"\n🎬 Processant animes...")
        for _, row in animes_df.iterrows():
            anime = Anime(row['anime_id'], row['name'], row['members'])
            anime.genre = row['genre']
            self.animes_dict[row['anime_id']] = anime
        
        print(f"   ✓ {len(self.animes_dict)} animes processats")
        
        # Crear objectes User
        print(f"\n👥 Processant usuaris...")
        for _, row in self.ratings_df.iterrows():
            user_id = row['user_id']
            anime_id = row['anime_id']
            rating = row['rating']
            
            user = User(user_id, anime_id, rating)
            
            if user_id not in self.users_dict:
                self.users_dict[user_id] = []
            self.users_dict[user_id].append(user)
        
        print(f"   ✓ {len(self.users_dict)} usuaris processats")
        
        # Crear pivot table
        print(f"\n📊 Creant pivot table...")
        self.userRatings_pivot = self.ratings_df.pivot_table(
            index='user_id', 
            columns='name', 
            values='rating'
        )
        print(f"   ✓ Pivot table creada: {self.userRatings_pivot.shape}")
        
        # Calcular matriu de correlacions amb un mínim de 50 en lloc de 100
        print(f"\n🔗 Calculant matriu de correlacions...")
        self.corrMatrix = self.userRatings_pivot.corr(method='pearson', min_periods=50)  # Baixat a 50
        print(f"   ✓ Matriu de correlacions calculada: {self.corrMatrix.shape}")
        
        # Calcular estadístiques
        print(f"\n📈 Calculant estadístiques...")
        self.animeStats = self.ratings_df.groupby('name').agg({'rating': np.size})
        
        # Calcular popularitat i rating mitjà
        self._calculate_anime_stats()
        
        print(f"   ✓ Estadístiques calculades")
        
        print(f"\n✅ Totes les dades processades correctament!")
    
    def get_model_info(self):
        """
        Retorna informació sobre el model actual
        
        Returns:
            dict: Informació del model (versió, temps de càrrega, estadístiques)
        """
        return {
            'version': int(self.current_model_version) if self.current_model_version else 0,
            'loaded_at': self.model_load_time.isoformat() if self.model_load_time else None,
            'num_animes': len(self.animes_dict),
            'num_users': len(self.users_dict),
            'num_ratings': len(self.ratings_df) if self.ratings_df is not None else 0,
            'data_changed': self.has_data_changed()
        }
    
    def search_anime_exact(self, query):
        """
        Cerca animes que coincideixin exactament o parcialment amb la query
        
        Returns:
            list: Llista d'animes que coincideixen
        """
        query_lower = query.lower()
        matches = []
        
        for anime_name in self.userRatings_pivot.columns:
            anime_name_lower = anime_name.lower()
            
            # Coincidència exacta
            if anime_name_lower == query_lower:
                return [{'name': anime_name, 'match_type': 'exact'}]
            
            # Coincidència parcial
            if query_lower in anime_name_lower:
                anime_info = self.ratings_df[self.ratings_df['name'] == anime_name].iloc[0]
                matches.append({
                    'name': anime_name,
                    'genre': str(anime_info.get('genre', 'Unknown')),
                    'match_type': 'partial'
                })
        
        return matches
    
    def get_recommendations_adjusted(self, anime_name, user_rating=5, num_recommendations=6):
        """
        Obté recomanacions ajustades segons la valoració de l'usuari
        
        - Si rating >= 4: Retorna animes similars
        - Si rating <= 2: Retorna animes diferents (correlació negativa o baixa)
        - Si rating = 3: Retorna animes moderadament similars
        """
        
        # Verificar que l'anime existeix
        if anime_name not in self.userRatings_pivot.columns:
            matching = [col for col in self.userRatings_pivot.columns if anime_name.lower() in col.lower()]
            if not matching:
                return None
            anime_name = matching[0]
        
        # Obtenir correlacions
        anime_ratings = self.userRatings_pivot[anime_name]
        similar_animes = self.userRatings_pivot.corrwith(anime_ratings)
        similar_animes = similar_animes.dropna()
        
        # Crear DataFrame amb correlacions
        df = pd.DataFrame(similar_animes, columns=['similarity'])
        
        # Filtrar per popularitat (mínim 50 valoracions)
        popular_animes = self.animeStats['rating'] >= 50  # Baixat a 50
        df = self.animeStats[popular_animes].join(df)
        df = df.dropna()
        
        # Afegir rating mitjà i popularitat
        if self.animeAvgRating is not None:
            df = df.join(self.animeAvgRating.rename('avg_rating'))
        if self.animePopularity is not None:
            df = df.join(self.animePopularity.rename('popularity'))
        
        # Eliminar l'anime actual dels resultats
        df = df[df.index != anime_name]
        
        # AJUSTAR SEGONS LA VALORACIÓ DE L'USUARI
        if user_rating >= 4:
            # Li agrada: retornar els més similars amb bon rating
            df['score'] = df['similarity'] * 0.7 + (df.get('avg_rating', 7) / 10) * 0.3
            df = df.sort_values('score', ascending=False)
            
        elif user_rating <= 2:
            # No li agrada: retornar animes diferents (correlació baixa o negativa) però populars
            # Prioritzar animes amb correlació baixa però bon rating mitjà
            df['difference_score'] = (1 - abs(df['similarity'])) * 0.5 + (df.get('avg_rating', 7) / 10) * 0.5
            df = df[df['similarity'] < 0.3]  # Només animes poc correlacionats
            df = df.sort_values('difference_score', ascending=False)
            
        else:  # rating = 3
            # Neutral: animes moderadament similars
            df = df[(df['similarity'] > 0.2) & (df['similarity'] < 0.6)]
            df['score'] = df['similarity'] * 0.5 + (df.get('avg_rating', 7) / 10) * 0.5
            df = df.sort_values('score', ascending=False)
        
        # Obtenir top recomanacions
        top_recommendations = df.head(num_recommendations)
        
        recommendations = []
        for anime_name_rec in top_recommendations.index:
            anime_info = self.ratings_df[self.ratings_df['name'] == anime_name_rec].iloc[0]
            
            # Obtenir correlació i score
            correlation = top_recommendations.loc[anime_name_rec, 'similarity']
            avg_rating = top_recommendations.loc[anime_name_rec].get('avg_rating', anime_info.get('rating', 0))
            
            recommendations.append({
                "title": str(anime_name_rec),
                "score": float(round(avg_rating, 1)) if pd.notna(avg_rating) else 0.0,
                "genre": str(anime_info.get('genre', 'Unknown')),
                "year": None,
                "correlation": float(round(correlation, 2)) if pd.notna(correlation) else 0.0
            })
        
        return recommendations
    
    def get_recommendations(self, anime_name, user_rating=None, num_recommendations=6):
        """
        Versió legacy per compatibilitat - redirigeix a get_recommendations_adjusted
        """
        return self.get_recommendations_adjusted(anime_name, user_rating or 5, num_recommendations)
    
    def get_recommendations_for_user(self, user_ratings_dict, num_recommendations=10):
        """
        Obté recomanacions basades en múltiples valoracions d'un usuari
        """
        simCandidates = pd.Series(dtype=float)
        
        for anime_name, rating in user_ratings_dict.items():
            if anime_name not in self.corrMatrix.columns:
                matching = [col for col in self.corrMatrix.columns if anime_name.lower() in col.lower()]
                if not matching:
                    print(f"Anime '{anime_name}' no trobat")
                    continue
                anime_name = matching[0]
            
            sims = self.corrMatrix[anime_name].dropna()
            
            # Ajustar segons la valoració
            if rating >= 4:
                # Li agrada: mantenir correlacions positives
                sims = sims.map(lambda x: x * rating)
            elif rating <= 2:
                # No li agrada: invertir correlacions
                sims = sims.map(lambda x: -x * (6 - rating))
            else:
                # Neutral: ponderar menys
                sims = sims.map(lambda x: x * rating * 0.5)
            
            simCandidates = pd.concat([simCandidates, sims])
        
        simCandidates = simCandidates.groupby(simCandidates.index).sum()
        simCandidates = simCandidates.sort_values(ascending=False)
        
        # Eliminar animes ja valorats
        for anime_name in user_ratings_dict.keys():
            if anime_name in simCandidates.index:
                simCandidates = simCandidates.drop(anime_name)
        
        top_recommendations = simCandidates.head(num_recommendations)
        
        recommendations = []
        for anime_name_rec, similarity_score in top_recommendations.items():
            anime_info = self.ratings_df[self.ratings_df['name'] == anime_name_rec].iloc[0]
            
            recommendations.append({
                "title": str(anime_name_rec),
                "score": float(round(anime_info.get('rating', 0), 1)) if pd.notna(anime_info.get('rating', 0)) else 0.0,
                "genre": str(anime_info.get('genre', 'Unknown')),
                "year": None,
                "correlation": float(round(similarity_score / sum(user_ratings_dict.values()), 2))
            })
        
        return recommendations
    
    def get_all_animes(self):
        """Retorna tots els animes disponibles"""
        animes_list = []
        seen_names = set()
        
        for _, row in self.ratings_df[['name', 'genre']].drop_duplicates('name').iterrows():
            if row['name'] not in seen_names:
                seen_names.add(row['name'])
                animes_list.append({
                    "name": str(row['name']),
                    "genre": str(row['genre'])
                })
        
        return sorted(animes_list, key=lambda x: x['name'])
    
    def search_anime(self, query):
        """Cerca animes pel nom"""
        query_lower = query.lower()
        results = []
        
        for anime_name in self.userRatings_pivot.columns:
            if query_lower in anime_name.lower():
                anime_info = self.ratings_df[self.ratings_df['name'] == anime_name].iloc[0]
                results.append({
                    "name": str(anime_name),
                    "genre": str(anime_info.get('genre', 'Unknown'))
                })
        
        return results[:20]
    
    def list_available_models(self):
        """Llista tots els models disponibles al directori model/"""
        if not self.model_dir.exists():
            return []
        
        models = []
        for file in sorted(self.model_dir.glob('corr_matrix_v*.pkl')):
            try:
                version_str = file.stem.split('_v')[1]
                version = int(version_str)
                size_mb = file.stat().st_size / (1024 * 1024)
                models.append({
                    'version': version,
                    'path': str(file),
                    'size_mb': round(size_mb, 2)
                })
            except (IndexError, ValueError):
                continue
        
        return models
