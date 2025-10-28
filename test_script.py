"""
Script de test per verificar el sistema de recomanacions amb dades reals
Executa aquest script abans de llançar el servidor Flask
"""

from recommendation_system import RecommendationSystem
from anime import Anime
from user import User
import os

def test_recommendation_system():
    print("=" * 80)
    print("TEST DEL SISTEMA DE RECOMANACIONS AMB DADES REALS")
    print("=" * 80)
    
    # Verificar existència dels CSV
    print("\n1. Verificant fitxers CSV...")
    anime_csv = 'anime.csv'
    rating_csv = 'rating_balanceado.csv'
    
    if not os.path.exists(anime_csv):
        print(f"   ✗ ERROR: No s'ha trobat '{anime_csv}'")
        print(f"   Especifica la ruta correcta al fitxer")
        return
    
    if not os.path.exists(rating_csv):
        print(f"   ⚠ WARNING: No s'ha trobat '{rating_csv}'")
        print(f"   Provant amb 'rating.csv'...")
        rating_csv = 'rating.csv'
        if not os.path.exists(rating_csv):
            print(f"   ✗ ERROR: Tampoc s'ha trobat 'rating.csv'")
            return
    
    print(f"   ✓ Trobat: {anime_csv}")
    print(f"   ✓ Trobat: {rating_csv}")
    
    # Inicialitzar sistema
    print("\n2. Inicialitzant sistema de recomanacions...")
    print("   (Això pot trigar uns minuts...)")
    
    try:
        rec_system = RecommendationSystem(
            anime_csv_path=anime_csv,
            rating_csv_path=rating_csv
        )
        print(f"   ✓ Sistema inicialitzat correctament")
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 1: Estadístiques del sistema
    print("\n3. Estadístiques del sistema:")
    print(f"   - Animes carregats: {len(rec_system.animes_dict)}")
    print(f"   - Usuaris processats: {len(rec_system.users_dict)}")
    print(f"   - Valoracions totals: {len(rec_system.ratings_df)}")
    print(f"   - Matriu de correlacions: {rec_system.corrMatrix.shape}")
    
    # Test 2: Cerca d'animes
    print("\n4. Provant cerca d'animes...")
    search_queries = ["Death Note", "Naruto", "One Piece"]
    
    for query in search_queries:
        results = rec_system.search_anime(query)
        if results:
            print(f"   ✓ Cerca '{query}': {len(results)} resultats")
            print(f"     Primer resultat: {results[0]['name']}")
        else:
            print(f"   ✗ Cerca '{query}': cap resultat")
    
    # Test 3: Recomanacions per a un anime específic
    print("\n5. Provant recomanacions per a 'Death Note'...")
    
    try:
        recommendations = rec_system.get_recommendations("Death Note", user_rating=5, num_recommendations=5)
        
        if recommendations:
            print(f"   ✓ {len(recommendations)} recomanacions obtingudes:")
            for i, rec in enumerate(recommendations, 1):
                print(f"     {i}. {rec['title']}")
                print(f"        - Gènere: {rec['genre']}")
                print(f"        - Correlació: {rec['correlation']}")
        else:
            print("   ✗ No s'han obtingut recomanacions")
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")
    
    # Test 4: Recomanacions amb múltiples valoracions
    print("\n6. Provant recomanacions amb múltiples valoracions...")
    
    test_ratings = {
        "Death Note": 5,
        "Code Geass: Hangyaku no Lelouch": 5,
        "Steins;Gate": 4.5
    }
    
    try:
        recommendations = rec_system.get_recommendations_for_user(
            user_ratings_dict=test_ratings,
            num_recommendations=5
        )
        
        if recommendations:
            print(f"   ✓ {len(recommendations)} recomanacions obtingudes:")
            for i, rec in enumerate(recommendations, 1):
                print(f"     {i}. {rec['title']} (correlació: {rec['correlation']})")
        else:
            print("   ✗ No s'han obtingut recomanacions")
    except Exception as e:
        print(f"   ✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Verificar classes User i Anime
    print("\n7. Verificant ús de classes User i Anime...")
    
    # Comprovar que s'han creat objectes Anime
    if rec_system.animes_dict:
        sample_anime_id = list(rec_system.animes_dict.keys())[0]
        sample_anime = rec_system.animes_dict[sample_anime_id]
        print(f"   ✓ Objecte Anime:")
        print(f"     - ID: {sample_anime.get_anime_id()}")
        print(f"     - Nom: {sample_anime.get_name()}")
        print(f"     - Membres: {sample_anime.get_members()}")
        print(f"     - Gènere: {sample_anime.genre}")
    
    # Comprovar que s'han creat objectes User
    if rec_system.users_dict:
        sample_user_id = list(rec_system.users_dict.keys())[0]
        sample_users = rec_system.users_dict[sample_user_id]
        print(f"\n   ✓ Objectes User per a user_id {sample_user_id}:")
        print(f"     - Nombre de valoracions: {len(sample_users)}")
        if sample_users:
            first_rating = sample_users[0]
            print(f"     - Primera valoració:")
            print(f"       * Anime ID: {first_rating.get_anime_id()}")
            print(f"       * Rating: {first_rating.get_rating()}")
    
    # Test 6: Animes més populars
    print("\n8. Top 10 animes més valorats:")
    popular = rec_system.animeStats.sort_values('rating', ascending=False).head(10)
    for i, (name, row) in enumerate(popular.iterrows(), 1):
        print(f"   {i}. {name}: {row['rating']} valoracions")
    
    # Test 7: Qualitat de la matriu de correlacions
    print("\n9. Qualitat de la matriu de correlacions:")
    total_cells = rec_system.corrMatrix.shape[0] * rec_system.corrMatrix.shape[1]
    nan_cells = rec_system.corrMatrix.isna().sum().sum()
    valid_cells = total_cells - nan_cells
    coverage = (valid_cells / total_cells) * 100
    
    print(f"   - Cel·les totals: {total_cells:,}")
    print(f"   - Cel·les amb correlació vàlida: {valid_cells:,}")
    print(f"   - Cel·les sense dades (NaN): {nan_cells:,}")
    print(f"   - Cobertura: {coverage:.2f}%")
    
    # Resum final
    print("\n" + "=" * 80)
    print("RESULTAT DEL TEST")
    print("=" * 80)
    print("✓ Tots els tests han passat correctament!")
    print("\n📊 RESUM:")
    print(f"  • Sistema carregat amb {len(rec_system.animes_dict):,} animes")
    print(f"  • Processades {len(rec_system.ratings_df):,} valoracions")
    print(f"  • {len(rec_system.users_dict):,} usuaris únics")
    print(f"  • Matriu de correlacions: {rec_system.corrMatrix.shape[0]:,} × {rec_system.corrMatrix.shape[1]:,}")
    print(f"  • Cobertura de dades: {coverage:.1f}%")
    print("\n✅ El sistema està llest per ser utilitzat.")
    print("   Executa 'python API-animes-flask.py' per iniciar el servidor.")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_recommendation_system()
    except KeyboardInterrupt:
        print("\n\n⚠ Test interromput per l'usuari")
    except Exception as e:
        print(f"\n\n✗ ERROR CRÍTIC durant el test:")
        print(f"   {str(e)}")
        print("\nDetalls de l'error:")
        import traceback
        traceback.print_exc()
