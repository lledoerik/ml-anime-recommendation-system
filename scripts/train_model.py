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
    RATING_CSV = DATA_DIR / 'cleaned_data.csv'
    
    print("\n" + "="*70)
    print("🎬 ENTRENAMENT DEL MODEL DE RECOMANACIONS D'ANIMES")
    print("="*70)
    
    if not ANIME_CSV.exists():
        print(f"\n❌ ERROR: No s'ha trobat {ANIME_CSV}")
        return False
    
    if not RATING_CSV.exists():
        print(f"\n❌ ERROR: No s'ha trobat {RATING_CSV}")
        return False
    
    print(f"\n✓ Fitxers trobats")
    
    try:
        print(f"\n🚀 Iniciant entrenament...\n")
        
        rec_system = RecommendationSystem.__new__(RecommendationSystem)
        rec_system.animes_dict = {}
        rec_system.users_dict = {}
        rec_system.ratings_df = None
        rec_system.userRatings_pivot = None
        rec_system.corrMatrix = None
        rec_system.animeStats = None
        rec_system.model_dir = root_dir / 'model'
        rec_system.anime_csv_path = ANIME_CSV
        rec_system.rating_csv_path = RATING_CSV
        rec_system.model_dir.mkdir(exist_ok=True)
        rec_system.current_model_version = None
        rec_system.model_load_time = None
        rec_system.data_files_hash = None
        
        rec_system.train_model(save=True)
        
        print("\n" + "="*70)
        print("✅ MODEL ENTRENAT I GUARDAT!")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    train_new_model()
