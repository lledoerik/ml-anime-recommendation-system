"""
Script per entrenar el model de recomanacions

Executa aquest script per generar la matriu de correlacions
i guardar-la en un fitxer PKL versionat.

Ús:
    python scripts/train_model.py
"""

import sys
from pathlib import Path

# Afegir el directori arrel al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.recommendation_system import RecommendationSystem


def train_new_model():
    """
    Entrena un nou model i el guarda amb versionat automàtic
    """
    DATA_DIR = root_dir / 'data'
    ANIME_CSV = DATA_DIR / 'anime.csv'
    
    # Provar diferents noms per al fitxer de ratings
    possible_rating_files = [
        'rating_balanceado.csv',
        'cleaned_data.csv', 
        'rating.csv'
    ]
    
    RATING_CSV = None
    for filename in possible_rating_files:
        test_path = DATA_DIR / filename
        if test_path.exists():
            RATING_CSV = test_path
            print(f"✓ Utilitzant fitxer de ratings: {filename}")
            break
    
    if RATING_CSV is None:
        print(f"\n❌ ERROR: No s'ha trobat cap fitxer de ratings a {DATA_DIR}")
        print(f"   Fitxers cercats: {', '.join(possible_rating_files)}")
        return False
    
    print("\n" + "="*70)
    print("🎬 ENTRENAMENT DEL MODEL DE RECOMANACIONS D'ANIMES")
    print("="*70)
    
    if not ANIME_CSV.exists():
        print(f"\n❌ ERROR: No s'ha trobat {ANIME_CSV}")
        return False
    
    print(f"\n✓ Fitxers trobats:")
    print(f"   - {ANIME_CSV}")
    print(f"   - {RATING_CSV}")
    
    # Comprovar mida dels fitxers
    anime_size = ANIME_CSV.stat().st_size / (1024 * 1024)
    rating_size = RATING_CSV.stat().st_size / (1024 * 1024)
    
    print(f"\n📊 Mida dels fitxers:")
    print(f"   - anime.csv: {anime_size:.1f} MB")
    print(f"   - ratings: {rating_size:.1f} MB")
    
    # Avís si el fitxer és molt gran
    if rating_size > 100:
        print(f"\n⚠️  AVÍS: El fitxer de ratings és gran ({rating_size:.1f} MB)")
        print(f"   L'entrenament pot trigar diversos minuts...")
    
    try:
        print(f"\n🚀 Iniciant entrenament...\n")
        
        # Crear una instància temporal només per entrenar
        rec_system = RecommendationSystem.__new__(RecommendationSystem)
        rec_system.animes_dict = {}
        rec_system.users_dict = {}
        rec_system.ratings_df = None
        rec_system.userRatings_pivot = None
        rec_system.corrMatrix = None
        rec_system.animeStats = None
        rec_system.animePopularity = None
        rec_system.animeAvgRating = None
        rec_system.model_dir = root_dir / 'model'
        rec_system.anime_csv_path = ANIME_CSV
        rec_system.rating_csv_path = RATING_CSV
        rec_system.model_dir.mkdir(exist_ok=True)
        rec_system.current_model_version = None
        rec_system.model_load_time = None
        rec_system.data_files_hash = None
        
        # Entrenar i guardar
        rec_system.train_model(save=True)
        
        print("\n" + "="*70)
        print("✅ MODEL ENTRENAT I GUARDAT!")
        print("="*70)
        print("\n🎉 El model s'ha entrenat correctament!")
        print("   L'API el detectarà i carregarà automàticament en 30 segons.")
        print("   O pots reiniciar l'aplicació per carregar-lo immediatament.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Donar consells segons l'error
        if "encoding" in str(e).lower():
            print("\n💡 CONSELL: Sembla un problema d'encoding.")
            print("   Prova de convertir els CSV a UTF-8:")
            print("   iconv -f ISO-8859-1 -t UTF-8 data/anime.csv > data/anime_utf8.csv")
        elif "memory" in str(e).lower():
            print("\n💡 CONSELL: Problema de memòria.")
            print("   Considera reduir la mida del dataset amb data_cleaner.py")
        
        return False


if __name__ == "__main__":
    import time
    
    start_time = time.time()
    
    if train_new_model():
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Temps total: {elapsed_time:.1f} segons")
    else:
        print("\n❌ L'entrenament ha fallat. Revisa els errors anteriors.")
