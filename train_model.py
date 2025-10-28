"""
Script per entrenar el model de recomanacions

Executa aquest script per generar la matriu de correlacions
i guardar-la en un fitxer PKL versionat.

Ús:
    python train_model.py
"""

from recommendation_system import RecommendationSystem
from pathlib import Path
import sys


def train_new_model():
    """
    Entrena un nou model i el guarda amb versionat automàtic
    """
    # Configurar les rutes dels fitxers CSV
    DATA_DIR = Path(__file__).resolve().parent / 'data'
    ANIME_CSV = DATA_DIR / 'anime.csv'
    RATING_CSV = DATA_DIR / 'rating_balanceado.csv'  # O 'cleaned_data.csv'
    
    print("\n" + "="*70)
    print("🎬 ENTRENAMENT DEL MODEL DE RECOMANACIONS D'ANIMES")
    print("="*70)
    
    # Verificar que existeixen els fitxers
    if not ANIME_CSV.exists():
        print(f"\n❌ ERROR: No s'ha trobat {ANIME_CSV}")
        print("   Assegura't que el fitxer anime.csv existeix al directori 'data/'")
        return False
    
    if not RATING_CSV.exists():
        print(f"\n❌ ERROR: No s'ha trobat {RATING_CSV}")
        print("   Assegura't que el fitxer de valoracions existeix al directori 'data/'")
        print("\n💡 Consell: Executa primer data_cleaner.py per generar cleaned_data.csv")
        return False
    
    print(f"\n✓ Fitxers trobats:")
    print(f"  - {ANIME_CSV}")
    print(f"  - {RATING_CSV}")
    
    try:
        # Crear una instància temporal només per entrenar
        # (No intentarà carregar cap model perquè usarem un mètode especial)
        print(f"\n🚀 Iniciant entrenament del model...")
        print(f"   ATENCIÓ: Aquest procés pot trigar uns minuts amb datasets grans\n")
        
        # Crear un sistema buit sense intentar carregar model
        rec_system = RecommendationSystem.__new__(RecommendationSystem)
        rec_system.animes_dict = {}
        rec_system.users_dict = {}
        rec_system.ratings_df = None
        rec_system.userRatings_pivot = None
        rec_system.corrMatrix = None
        rec_system.animeStats = None
        rec_system.model_dir = Path('model')
        rec_system.anime_csv_path = ANIME_CSV
        rec_system.rating_csv_path = RATING_CSV
        rec_system.model_dir.mkdir(exist_ok=True)
        
        # Entrenar el model
        rec_system.train_model(save=True)
        
        print("\n" + "="*70)
        print("✅ MODEL ENTRENAT I GUARDAT CORRECTAMENT!")
        print("="*70)
        print("\n📋 Models disponibles:")
        
        # Llistar tots els models
        models = rec_system.list_available_models()
        for model in models:
            print(f"  - v{model['version']}: {model['size_mb']} MB ({model['path']})")
        
        print("\n🚀 Ara pots executar l'aplicació Flask:")
        print("   python app.py")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durant l'entrenament: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def list_models():
    """
    Llista tots els models disponibles
    """
    model_dir = Path('model')
    
    if not model_dir.exists() or not any(model_dir.glob('corr_matrix_v*.pkl')):
        print("\n📁 No hi ha cap model entrenat al directori 'model/'")
        print("   Executa 'python train_model.py' per generar-ne un")
        return
    
    print("\n" + "="*70)
    print("📋 MODELS DISPONIBLES")
    print("="*70)
    
    models = []
    for file in sorted(model_dir.glob('corr_matrix_v*.pkl')):
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
    
    if not models:
        print("\n❌ No s'han trobat models vàlids")
        return
    
    latest = max(models, key=lambda x: x['version'])
    
    for model in models:
        is_latest = " (ACTUAL)" if model['version'] == latest['version'] else ""
        print(f"\n  📦 Versió {model['version']}{is_latest}")
        print(f"     Mida: {model['size_mb']} MB")
        print(f"     Ruta: {model['path']}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_models()
    else:
        print("\n🎯 Opcions:")
        print("  1. Entrenar nou model")
        print("  2. Llistar models disponibles")
        print("  3. Sortir")
        
        choice = input("\nSelecciona una opció (1-3): ").strip()
        
        if choice == '1':
            train_new_model()
        elif choice == '2':
            list_models()
        elif choice == '3':
            print("Sortint...")
        else:
            print("Opció no vàlida")
