from anime import Anime
from user import User
import pandas as pd
import numpy as np
import pickle
import os
from pathlib import Path


class RecommendationSystem:
    def __init__(self, anime_csv_path='data/anime.csv', rating_csv_path='data/rating_balanceado.csv',
                 model_dir='model'):
        """
        Inicialitza el sistema de recomanacions carregant les dades dels CSV
        """
        self.animes_dict = {}  # Diccionari d'objectes Anime
        self.users_dict = {}  # Diccionari d'objectes User
        self.ratings_df = None
        self.userRatings_pivot = None
        self.corrMatrix = None
        self.animeStats = None
        self.model_dir = Path(model_dir)
        self.anime_csv_path = anime_csv_path
        self.rating_csv_path = rating_csv_path

        # Crear directori model si no existeix
        self.model_dir.mkdir(exist_ok=True)

        # Intentar carregar model entrenat
        if not self._load_latest_model():
            print("\n" + "=" * 70)
            print("⚠️  CAP MODEL ENTRENAT TROBAT")
            print("=" * 70)
            print("\nEl directori 'model/' està buit o no conté models vàlids.")
            print("\n🔧 Per generar el model, executa:")
            print("   python train_model.py")
            print("\nO des de Python:")
            print("   rec_system = RecommendationSystem(...)")
            print("   rec_system.train_model()")
            print("=" * 70)
            raise FileNotFoundError(
                "No s'ha trobat cap model entrenat. "
                "Executa train_model() o train_model.py abans d'usar el sistema."
            )

    def _get_latest_version(self):
        """
        Troba l'última versió del model disponible
        """
        if not self.model_dir.exists():
            return 0

        versions = []
        for file in self.model_dir.glob('corr_matrix_v*.pkl'):
            try:
                # Extreure número de versió del nom del fitxer
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
        Retorna True si s'ha carregat correctament, False altrament
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

            print(f"✅ Model v{latest_version} carregat correctament!")
            print(f"   - {len(self.animes_dict)} animes")
            print(f"   - {len(self.users_dict)} usuaris")
            print(f"   - Matriu de correlacions: {self.corrMatrix.shape}")

            return True

        except Exception as e:
            print(f"❌ Error carregant el model: {str(e)}")
            return False

    def train_model(self, save=True):
        """
        Entrena el model calculant la matriu de correlacions i totes les estructures necessàries.
        Si save=True, guarda el model en un fitxer PKL amb versionat.

        Aquest procés pot trigar uns minuts amb datasets grans.
        """
        print("\n" + "=" * 70)
        print("🚀 INICIANT ENTRENAMENT DEL MODEL")
        print("=" * 70)

        # Carregar dades dels CSV
        self._load_data_for_training(self.anime_csv_path, self.rating_csv_path)

        if save:
            # Guardar el model amb la següent versió
            next_version = self._get_next_version()
            model_path = self.model_dir / f'corr_matrix_v{next_version}.pkl'

            print(f"\n💾 Guardant model v{next_version} a {model_path}...")

            model_data = {
                'animes_dict': self.animes_dict,
                'users_dict': self.users_dict,
                'ratings_df': self.ratings_df,
                'userRatings_pivot': self.userRatings_pivot,
                'corrMatrix': self.corrMatrix,
                'animeStats': self.animeStats,
                'version': next_version,
                'anime_csv_path': str(self.anime_csv_path),
                'rating_csv_path': str(self.rating_csv_path)
            }

            try:
                with open(model_path, 'wb') as f:
                    pickle.dump(model_data, f, protocol=pickle.HIGHEST_PROTOCOL)

                print(f"✅ Model v{next_version} guardat correctament!")
                print(f"   Mida del fitxer: {model_path.stat().st_size / (1024 * 1024):.1f} MB")

            except Exception as e:
                print(f"❌ Error guardant el model: {str(e)}")
                raise

        print("=" * 70)
        print("✅ ENTRENAMENT COMPLETAT!")
        print("=" * 70)

    def _load_data_for_training(self, anime_csv_path, rating_csv_path):
        """
        Carrega i processa les dades dels CSV seguint la lògica dels notebooks
        (Aquest és el codi original de load_data però renombrat per claredat)
        """
        print("\n📂 Carregant dades dels CSV...")

        # Llegir anime.csv
        a_cols = ['anime_id', 'name', 'genre', 'members']
        animes_df = pd.read_csv(anime_csv_path, sep=',', usecols=a_cols, encoding="ISO-8859-1")

        # Llegir cleaned_data.csv (o rating.csv si no tens el balancejat)
        ratings_df = pd.read_csv(rating_csv_path, sep=',', encoding="ISO-8859-1")

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

        # Crear objectes User amb les seves valoracions
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

        # Crear la pivot table (usuaris vs animes)
        print(f"\n📊 Creant pivot table (pot trigar uns minuts amb datasets grans)...")
        self.userRatings_pivot = self.ratings_df.pivot_table(
            index='user_id',
            columns='name',
            values='rating'
        )
        print(f"   ✓ Pivot table creada: {self.userRatings_pivot.shape}")

        # Calcular matriu de correlacions de Pearson
        print(f"\n🔗 Calculant matriu de correlacions (això pot trigar força)...")
        self.corrMatrix = self.userRatings_pivot.corr(method='pearson', min_periods=100)
        print(f"   ✓ Matriu de correlacions calculada: {self.corrMatrix.shape}")

        # Calcular estadístiques dels animes (nombre de valoracions)
        print(f"\n📈 Calculant estadístiques dels animes...")
        self.animeStats = self.ratings_df.groupby('name').agg({'rating': np.size})
        print(f"   ✓ Estadístiques calculades")

        print(f"\n✅ Totes les dades processades correctament!")

    def get_recommendations(self, anime_name, user_rating=None, num_recommendations=6):
        """
        Obté recomanacions basades en un anime concret
        Segueix la lògica de Animes_similares.ipynb
        """
        # Comprovar si l'anime existeix
        if anime_name not in self.userRatings_pivot.columns:
            # Intentar cerca parcial
            matching = [col for col in self.userRatings_pivot.columns if anime_name.lower() in col.lower()]
            if not matching:
                return None
            anime_name = matching[0]

        # Obtenir valoracions de l'anime
        anime_ratings = self.userRatings_pivot[anime_name]

        # Calcular similituds amb altres animes
        similar_animes = self.userRatings_pivot.corrwith(anime_ratings)
        similar_animes = similar_animes.dropna()

        # Crear DataFrame amb similituds
        df = pd.DataFrame(similar_animes, columns=['similarity'])

        # Filtrar per animes populars (mínim 100 valoracions)
        popular_animes = self.animeStats['rating'] >= 100
        df = self.animeStats[popular_animes].join(df)

        # Eliminar NaN i ordenar per similitud
        df = df.dropna()
        df = df.sort_values(['similarity'], ascending=False)

        # Excloure l'anime original
        df = df[df.index != anime_name]

        # Obtenir top N recomanacions
        top_recommendations = df.head(num_recommendations)

        # Preparar resultats amb informació completa
        recommendations = []
        for anime_name_rec in top_recommendations.index:
            # Buscar informació de l'anime
            anime_info = self.ratings_df[self.ratings_df['name'] == anime_name_rec].iloc[0]

            # Convertir tots els valors a tipus Python natius per JSON
            recommendations.append({
                "title": str(anime_name_rec),
                "score": float(round(anime_info.get('rating', 0), 1)) if pd.notna(anime_info.get('rating', 0)) else 0.0,
                "genre": str(anime_info.get('genre', 'Unknown')),
                "year": None,
                "correlation": float(round(top_recommendations.loc[anime_name_rec, 'similarity'], 2))
            })

        return recommendations

    def get_recommendations_for_user(self, user_ratings_dict, num_recommendations=10):
        """
        Obté recomanacions basades en múltiples valoracions d'un usuari
        Segueix la lògica de Anime.ipynb

        user_ratings_dict: dict amb {anime_name: rating}
        """
        simCandidates = pd.Series(dtype=float)

        for anime_name, rating in user_ratings_dict.items():
            # Comprovar si l'anime existeix
            if anime_name not in self.corrMatrix.columns:
                matching = [col for col in self.corrMatrix.columns if anime_name.lower() in col.lower()]
                if not matching:
                    print(f"Anime '{anime_name}' no trobat")
                    continue
                anime_name = matching[0]

            print(f'Afegint animes similars a {anime_name}...')

            # Obtenir similituds
            sims = self.corrMatrix[anime_name].dropna()

            # Ponderar per la valoració de l'usuari
            sims = sims.map(lambda x: x * rating)

            # Concatenar amb els candidats existents
            simCandidates = pd.concat([simCandidates, sims])

        # Agrupar per anime i sumar similituds
        simCandidates = simCandidates.groupby(simCandidates.index).sum()

        # Ordenar per similitud
        simCandidates = simCandidates.sort_values(ascending=False)

        # Eliminar els animes que l'usuari ja ha valorat
        for anime_name in user_ratings_dict.keys():
            if anime_name in simCandidates.index:
                simCandidates = simCandidates.drop(anime_name)

        # Obtenir top N
        top_recommendations = simCandidates.head(num_recommendations)

        # Preparar resultats amb conversió a tipus Python natius
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

        return results[:20]  # Limitar a 20 resultats

    def list_available_models(self):
        """
        Llista tots els models disponibles al directori model/
        """
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