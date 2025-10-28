from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from pathlib import Path

# Importar el sistema de recomanacions
from recommendation_system import RecommendationSystem

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)
app.config["DEBUG"] = True

# IMPORTANT: Canvia aquestes rutes per les teves rutes reals dels CSV
DATA_DIR = Path(__file__).resolve().parent / 'data'
ANIME_CSV = DATA_DIR / 'anime.csv'
RATING_CSV = DATA_DIR / 'rating_balanceado.csv'  # O 'rating.csv' si no tens el balancejat

print("Inicialitzant sistema de recomanacions...")
print(f"Cercant fitxers:")
print(f"  - {ANIME_CSV}")
print(f"  - {RATING_CSV}")

# Inicialitzar el sistema de recomanacions (pot trigar uns segons)
rec_system = RecommendationSystem(
    anime_csv_path=ANIME_CSV,
    rating_csv_path=RATING_CSV
)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Endpoint per obtenir recomanacions basades en un anime
    POST: { "anime": "Death Note", "rating": 4.5 }
    """
    try:
        data = request.get_json()
        anime_name = data.get('anime')
        rating = data.get('rating')
        
        if not anime_name:
            return jsonify({
                "error": "El paràmetre 'anime' és obligatori"
            }), 400
        
        # Obtenir recomanacions
        recommendations = rec_system.get_recommendations(
            anime_name=anime_name,
            user_rating=rating,
            num_recommendations=6
        )
        
        if recommendations is None:
            return jsonify({
                "error": f"No s'ha trobat l'anime '{anime_name}'. Prova amb una cerca més específica."
            }), 404
        
        return jsonify({
            "anime": anime_name,
            "user_rating": rating,
            "recommendations": recommendations
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Error intern del servidor: {str(e)}"
        }), 500

@app.route('/api/recommendations-multiple', methods=['POST'])
def get_recommendations_multiple():
    """
    Endpoint per obtenir recomanacions basades en múltiples animes valorats
    POST: { 
        "ratings": {
            "Death Note": 5,
            "Code Geass": 4.5,
            "Steins;Gate": 5
        }
    }
    """
    try:
        data = request.get_json()
        ratings = data.get('ratings')
        
        if not ratings or not isinstance(ratings, dict):
            return jsonify({
                "error": "El paràmetre 'ratings' és obligatori i ha de ser un diccionari"
            }), 400
        
        # Obtenir recomanacions
        recommendations = rec_system.get_recommendations_for_user(
            user_ratings_dict=ratings,
            num_recommendations=10
        )
        
        return jsonify({
            "user_ratings": ratings,
            "recommendations": recommendations
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": f"Error intern del servidor: {str(e)}"
        }), 500

@app.route('/api/animes', methods=['GET'])
def get_animes():
    """Retorna la llista de tots els animes disponibles"""
    try:
        animes = rec_system.get_all_animes()
        return jsonify({
            "animes": animes,
            "count": len(animes)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_anime():
    """Cerca animes pel nom"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                "error": "El paràmetre 'q' és obligatori"
            }), 400
            
        results = rec_system.search_anime(query)
        return jsonify({
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SERVIDOR FLASK INICIAT")
    print("="*60)
    print(f"Sistema carregat amb:")
    print(f"  - {len(rec_system.animes_dict)} animes")
    print(f"  - {len(rec_system.users_dict)} usuaris")
    print(f"\nAccedeix a: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
