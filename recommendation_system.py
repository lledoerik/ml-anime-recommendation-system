from anime import Anime
from user import User
import pandas as pd
import numpy as np

class RecommendationSystem:
    def __init__(self, anime_csv_path='data/anime.csv', rating_csv_path='data/rating_balanceado.csv'):
        """
        Inicialitza el sistema de recomanacions carregant les dades dels CSV
        """
        self.animes_dict = {}  # Diccionari d'objectes Anime
        self.users_dict = {}   # Diccionari d'objectes User
        self.ratings_df = None
        self.userRatings_pivot = None
        self.corrMatrix = None
        self.animeStats = None
        
        # Carregar dades
        self.load_data(anime_csv_path, rating_csv_path)
    
    def load_data(self, anime_csv_path, rating_csv_path):
        """
        Carrega i processa les dades dels CSV seguint la lògica dels notebooks
        """
        print("Carregant dades dels CSV...")
        
        # AQUÍ HAURÀS DE POSAR LA RUTA CORRECTA DELS TEUS CSV
        # Llegir anime.csv
        a_cols = ['anime_id', 'name', 'genre', 'members']
        animes_df = pd.read_csv(anime_csv_path, sep=',', usecols=a_cols, encoding="ISO-8859-1")
        
        # Llegir rating_balanceado.csv (o rating.csv si no tens el balancejat)
        ratings_df = pd.read_csv(rating_csv_path, sep=',', encoding="ISO-8859-1")
        
        # Merge de les dades
        self.ratings_df = pd.merge(animes_df, ratings_df)
        
        print(f"Dades carregades: {len(self.ratings_df)} valoracions")
        
        # Crear objectes Anime
        for _, row in animes_df.iterrows():
            anime = Anime(row['anime_id'], row['name'], row['members'])
            anime.genre = row['genre']
            self.animes_dict[row['anime_id']] = anime
            
        # Crear objectes User amb les seves valoracions
        for _, row in self.ratings_df.iterrows():
            user_id = row['user_id']
            anime_id = row['anime_id']
            rating = row['rating']
            
            user = User(user_id, anime_id, rating)
            
            if user_id not in self.users_dict:
                self.users_dict[user_id] = []
            self.users_dict[user_id].append(user)
        
        print(f"Processats {len(self.animes_dict)} animes i {len(self.users_dict)} usuaris")
        
        # Crear la pivot table (usuaris vs animes)
        print("Creant matriu de correlacions...")
        self.userRatings_pivot = self.ratings_df.pivot_table(
            index='user_id', 
            columns='name', 
            values='rating'
        )
        
        # Calcular matriu de correlacions de Pearson
        self.corrMatrix = self.userRatings_pivot.corr(method='pearson', min_periods=100)
        
        # Calcular estadístiques dels animes (nombre de valoracions)
        self.animeStats = self.ratings_df.groupby('name').agg({'rating': np.size})
        
        print("Sistema de recomanacions inicialitzat correctament!")
    
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
            
            recommendations.append({
                "title": anime_name_rec,
                "score": round(anime_info.get('rating', 0), 1) if pd.notna(anime_info.get('rating', 0)) else 0,
                "genre": anime_info.get('genre', 'Unknown'),
                "year": None,  # No tenim aquesta informació al CSV
                "correlation": round(top_recommendations.loc[anime_name_rec, 'similarity'], 2)
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
        
        # Preparar resultats
        recommendations = []
        for anime_name_rec, similarity_score in top_recommendations.items():
            anime_info = self.ratings_df[self.ratings_df['name'] == anime_name_rec].iloc[0]
            
            recommendations.append({
                "title": anime_name_rec,
                "score": round(anime_info.get('rating', 0), 1) if pd.notna(anime_info.get('rating', 0)) else 0,
                "genre": anime_info.get('genre', 'Unknown'),
                "year": None,
                "correlation": round(similarity_score / sum(user_ratings_dict.values()), 2)
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
                    "name": row['name'],
                    "genre": row['genre']
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
                    "name": anime_name,
                    "genre": anime_info.get('genre', 'Unknown')
                })
        
        return results[:20]  # Limitar a 20 resultats
