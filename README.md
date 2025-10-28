# 🎬 Sistema de Recomanacions d'Animes

Sistema intel·ligent de recomanacions basat en collaborative filtering amb correlació de Pearson.

## 📋 Índex

1. [Instal·lació](#instal·lació)
2. [Estructura del Projecte](#estructura-del-projecte)
3. [Flux de Treball](#flux-de-treball)
4. [Entrenament del Model](#entrenament-del-model)
5. [Executar l'Aplicació](#executar-l'aplicació)
6. [API Endpoints](#api-endpoints)
7. [Resolució de Problemes](#resolució-de-problemes)

---

## 🚀 Instal·lació

### 1. Requisits
```bash
pip install flask flask-cors pandas numpy
```

### 2. Estructura de Directoris
```
project/
├── data/
│   ├── anime.csv                    # Dataset d'animes
│   └── rating_balanceado.csv        # Dataset de valoracions (net)
├── model/                           # Models entrenats (es crea automàticament)
│   └── corr_matrix_v1.pkl          # Model entrenat
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── anime.py                         # Classe Anime
├── user.py                          # Classe User
├── recommendation_system.py         # Sistema principal
├── app.py                           # API Flask
├── train_model.py                   # Script d'entrenament
└── data_cleaner.py                  # Script de neteja de dades
```

---

## 🔄 Flux de Treball

### **Pas 1: Netejar les Dades (Opcional)**

Si tens el fitxer `rating.csv` original (amb valoracions -1):

```bash
python data_cleaner.py
```

Això generarà `cleaned_data.csv` o `rating_balanceado.csv` amb:
- Sense valoracions -1
- Usuaris amb mínim 100 valoracions
- Animes amb mínim 50 valoracions

### **Pas 2: Entrenar el Model** ⚠️ **OBLIGATORI LA PRIMERA VEGADA**

```bash
python train_model.py
```

**Què fa aquest script?**
- Carrega les dades dels CSV
- Crea la pivot table (usuaris × animes)
- Calcula la matriu de correlacions de Pearson
- Guarda tot en un fitxer PKL versionat

**Output:**
```
📦 Model v1 guardat a: model/corr_matrix_v1.pkl
   Mida del fitxer: 45.3 MB
```

⏱️ **Temps estimat:** 2-10 minuts segons la mida del dataset

### **Pas 3: Executar l'Aplicació**

```bash
python app.py
```

Accedeix a: `http://localhost:5000`

---

## 🎯 Entrenament del Model

### Opcions del Script

```bash
# Entrenar nou model (opció interactiva)
python train_model.py

# Llistar models disponibles
python train_model.py --list
```

### Versionat Automàtic

Cada cop que entrenes el model, es crea una nova versió:
- Primera vegada: `corr_matrix_v1.pkl`
- Segona vegada: `corr_matrix_v2.pkl`
- I així successivament...

L'aplicació **sempre carrega l'última versió** automàticament.

### Quan Reentrenar?

Reentrena el model quan:
- Afegeixes noves dades al CSV
- Canvies els paràmetres de filtratge
- Vols experimentar amb diferents configuracions

---

## 🌐 API Endpoints

### 1. **Obtenir Recomanacions d'un Anime**

**POST** `/api/recommendations`

```json
{
  "anime": "Death Note",
  "rating": 4.5
}
```

**Response:**
```json
{
  "anime": "Death Note",
  "user_rating": 4.5,
  "recommendations": [
    {
      "title": "Code Geass",
      "score": 8.7,
      "genre": "Action, Drama",
      "year": null,
      "correlation": 0.87
    },
    ...
  ]
}
```

### 2. **Recomanacions per Múltiples Animes**

**POST** `/api/recommendations-multiple`

```json
{
  "ratings": {
    "Death Note": 5,
    "Code Geass": 4.5,
    "Steins;Gate": 5
  }
}
```

### 3. **Llistar Tots els Animes**

**GET** `/api/animes`

### 4. **Cercar Anime**

**GET** `/api/search?q=death`

### 5. **Llistar Models Disponibles**

**GET** `/api/models`

---

## ⚙️ Funcionament Intern

### Sistema de Càrrega

```python
# 1. L'app.py intenta carregar el model
rec_system = RecommendationSystem(...)

# 2. RecommendationSystem busca l'última versió
latest_version = _get_latest_version()  # Troba v3 si existeix

# 3. Carrega el PKL
model_data = pickle.load('model/corr_matrix_v3.pkl')

# 4. Restaura totes les estructures
self.corrMatrix = model_data['corrMatrix']
self.userRatings_pivot = model_data['userRatings_pivot']
self.animeStats = model_data['animeStats']
# ...
```

### Avantatges

✅ **Rapidesa:** Càrrega en segons vs minuts
✅ **Versionat:** Historial de models
✅ **Consistència:** Mateixa matriu de correlacions sempre
✅ **Fiabilitat:** Sense JSON serialization errors

---

## 🛠️ Resolució de Problemes

### Error: "No s'ha trobat cap model entrenat"

**Causa:** El directori `model/` està buit

**Solució:**
```bash
python train_model.py
```

### Error: "Object of type np.float64 is not JSON serializable"

**Causa:** Aquest error ja està resolt en la nova versió

**Què hem fet:**
- Convertim tots els valors a tipus Python natius (`float()`, `str()`, `int()`)
- Abans: `rating = anime_info.get('rating', 0)` → numpy.float64
- Ara: `rating = float(anime_info.get('rating', 0))` → Python float

### Error: "No s'ha trobat el fitxer anime.csv"

**Solució:**
1. Assegura't que els CSV estan a `data/anime.csv` i `data/rating_balanceado.csv`
2. Ajusta les rutes a `app.py` si cal

### L'aplicació triga molt a carregar

**Causa:** Està calculant les correlacions en temps real

**Solució:**
```bash
# 1. Atura l'app
Ctrl+C

# 2. Entrena el model
python train_model.py

# 3. Torna a executar
python app.py
```

### Vull esborrar models antics

```bash
# Veure models disponibles
python train_model.py --list

# Esborrar manualment
rm model/corr_matrix_v1.pkl
rm model/corr_matrix_v2.pkl
```

---

## 📊 Estadístiques del Sistema

Després d'entrenar, veuràs:

```
✅ MODEL ENTRENAT I GUARDAT CORRECTAMENT!
======================================================================
📋 Models disponibles:
  - v1: 45.3 MB (model/corr_matrix_v1.pkl)
  - v2: 46.1 MB (model/corr_matrix_v2.pkl)
  - v3: 45.8 MB (model/corr_matrix_v3.pkl) (ACTUAL)

🚀 Ara pots executar l'aplicació Flask:
   python app.py
======================================================================
```

---

## 💡 Consells

1. **Primera Execució:** Sempre entrena el model primer
2. **Desenvolupament:** Pots reentrenar quan vulguis sense perdre versions antigues
3. **Producció:** Usa sempre un model entrenat, mai calcular en temps real
4. **Depuració:** Comprova `model/` per veure quins models tens disponibles

---

## 🎓 Conceptes Clau

### Què conté el PKL?

```python
model_data = {
    'animes_dict': {...},          # Diccionari d'objectes Anime
    'users_dict': {...},           # Diccionari d'objectes User
    'ratings_df': DataFrame,       # Dataset complet
    'userRatings_pivot': DataFrame, # Matriu usuaris × animes
    'corrMatrix': DataFrame,       # Correlacions de Pearson
    'animeStats': DataFrame,       # Estadístiques per anime
    'version': 3,                  # Número de versió
}
```

### Per què guardar pivot i stats?

- **userRatings_pivot:** Triga molt a crear (pivot sobre milions de files)
- **corrMatrix:** Triga molt a calcular (correlacions entre milers d'animes)
- **animeStats:** Necessari per filtrar animes populars

Guardar-ho tot accelera la càrrega **x100** o més! 🚀

---

## 📝 Llicència

Projecte acadèmic de sistema de recomanacions d'animes.
