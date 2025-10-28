# 🎬 Sistema de Recomanacions d'Animes

Sistema intel·ligent de recomanacions basat en collaborative filtering amb correlació de Pearson. Inclou entrenament automàtic del model cada dia a les 2:30 AM.

## 📋 Característiques

✅ **Recomanacions intel·ligents** basades en correlació de Pearson
✅ **Entrenament automàtic** del model cada dia a les 2:30 AM
✅ **Sistema de versionat** de models (v1, v2, v3...)
✅ **Footer informatiu** amb versió del model en temps real
✅ **Càrrega ràpida** (2-3 segons vs 20 minuts!)
✅ **Entrenament en background** sense bloquejar l'aplicació
✅ **API REST** completa amb Flask
✅ **Interfície web** moderna i responsive

## 🚀 Instal·lació

### 1. Requisits
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Estructura de Directoris
```
ml-anime-recommendation-system/
├── README.md
├── requirements.txt
├── .gitignore
├── app.py                        # Punt d'entrada de l'aplicació
│
├── data/                         # Datasets
│   ├── anime.csv
│   └── rating_balanceado.csv
│
├── model/                        # Models entrenats (PKL)
│   ├── corr_matrix_v1.pkl
│   ├── corr_matrix_v2.pkl
│   └── ...
│
├── src/                          # Codi font principal
│   ├── __init__.py
│   ├── models/                   # Classes de dades
│   │   ├── __init__.py
│   │   ├── anime.py
│   │   └── user.py
│   └── recommendation_system.py  # Motor de recomanacions
│
├── scripts/                      # Scripts d'utilitat
│   ├── train_model.py            # Entrenar model
│   ├── train_auto.sh             # Script bash simplificat
│   └── data_cleaner.py           # Netejar dades
│
├── static/                       # Frontend
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── templates/                    # HTML templates
    └── index.html
```

## 🔄 Flux de Treball

### Pas 1: Netejar les Dades (Opcional)
Si tens el fitxer `rating.csv` original:
```bash
python scripts/data_cleaner.py
```

### Pas 2: Entrenar el Model ⚠️ OBLIGATORI LA PRIMERA VEGADA
```bash
# Opció 1: Script Python
python scripts/train_model.py

# Opció 2: Script bash simplificat
./scripts/train_auto.sh
```

**Output:**
```
📦 Model v1 guardat a: model/corr_matrix_v1.pkl
   Mida del fitxer: 45.3 MB
```

⏱️ **Temps estimat:** 5-10 minuts segons la mida del dataset

### Pas 3: Executar l'Aplicació
```bash
python app.py
```

Accedeix a: `http://localhost:5000`

## 🤖 Entrenament Automàtic

L'aplicació **comprova automàticament** cada dia a les **2:30 AM** si les dades han canviat.

**Funcionament:**
1. 🕐 A les 2:30 AM, l'scheduler es desperta
2. 🔍 Comprova si `anime.csv` o `rating_balanceado.csv` han canviat
3. 🚫 Si no han canviat → No fa res
4. ✅ Si han canviat → Entrena un model nou en **background**
5. 🔄 Quan acaba, **recarrega automàticament** el model nou
6. 👥 Els usuaris **no noten res** - segueixen usant el model anterior durant l'entrenament

**Avantatges:**
- ✅ **Zero downtime:** L'app no es para mai
- ✅ **Transparent:** Els usuaris no ho noten
- ✅ **Automàtic:** No cal intervenció manual
- ✅ **Versionat:** Es guarda cada versió (v1, v2, v3...)

## 🌐 API Endpoints

### 1. Obtenir Recomanacions
```bash
POST /api/recommendations
{
  "anime": "Death Note",
  "rating": 4.5
}
```

### 2. Recomanacions Múltiples
```bash
POST /api/recommendations-multiple
{
  "ratings": {
    "Death Note": 5,
    "Code Geass": 4.5
  }
}
```

### 3. Informació del Model ⭐ NOU
```bash
GET /api/model-info

Response:
{
  "version": 3,
  "loaded_at": "2024-10-28T12:30:45",
  "num_animes": 12294,
  "num_users": 73516,
  "num_ratings": 2156789,
  "data_changed": false,
  "training_in_progress": false
}
```

### 4. Altres Endpoints
```bash
GET  /api/animes              # Llistar tots els animes
GET  /api/search?q=death      # Cercar animes
GET  /api/models              # Llistar models disponibles
POST /api/train               # Forçar entrenament manual
```

## 📊 Footer amb Informació del Model

El footer mostra en temps real:
- 📦 **Versió del model** actual (v1, v2, v3...)
- 🎬 **Nombre d'animes** en el model
- 👥 **Nombre d'usuaris** en el model
- 📅 **Data de càrrega** del model
- 🔄 **Indicador d'entrenament** si s'està entrenant

**El footer s'actualitza automàticament cada 30 segons!**

## ⚙️ Com Funciona el Sistema

### 1. Càrrega Ràpida
```python
# En lloc de calcular cada vegada (20 minuts):
corrMatrix = userRatings_pivot.corr(...)  # ❌ Lent

# Carreguem del PKL (2-3 segons):
model_data = pickle.load('model/corr_matrix_v3.pkl')  # ✅ Ràpid
```

### 2. Versionat Automàtic
```
Primera vegada: corr_matrix_v1.pkl
Segona vegada:  corr_matrix_v2.pkl
Tercera vegada: corr_matrix_v3.pkl
...
```

L'app **sempre carrega l'última versió** automàticament.

### 3. Scheduler Automàtic
```python
# APScheduler executa check_and_retrain() cada dia a les 2:30 AM
scheduler.add_job(
    func=check_and_retrain,
    trigger=CronTrigger(hour=2, minute=30),
    id='daily_model_check'
)
```

### 4. Entrenament en Background
```python
# Threading per no bloquejar l'app
training_thread = threading.Thread(target=train_model_background)
training_thread.daemon = True
training_thread.start()

# Els usuaris segueixen usant model v3
# Mentre en background s'entrena v4
# Quan v4 està llest → switch automàtic
```

## 🛠️ Resolució de Problemes

### Error: "No s'ha trobat cap model entrenat"
```bash
python scripts/train_model.py
```

### L'app triga molt a carregar
Això vol dir que no tens cap model entrenat!
```bash
python scripts/train_model.py
```

### Vull esborrar models antics
```bash
rm model/corr_matrix_v1.pkl
rm model/corr_matrix_v2.pkl
# Mantén només la versió més recent
```

### Canviar l'hora de l'entrenament automàtic
Edita `app.py`:
```python
# Canvia aquesta línia:
trigger = CronTrigger(hour=2, minute=30)

# Per exemple, per executar-lo a les 3:45 AM:
trigger = CronTrigger(hour=3, minute=45)
```

## 💡 Conceptes Clau

### Threading vs Multiprocessing
**Threading (el que usem):**
- Múltiples tasques en el mateix procés
- Comparteixen memòria
- Més lleuger
- Ideal per I/O (com entrenar models)

**Multiprocessing:**
- Múltiples processos independents
- Memòria separada
- Més pesant
- Ideal per CPU-intensive tasks

### Scheduler (APScheduler)
Permet executar funcions en moments específics:
- `CronTrigger(hour=2, minute=30)` → Cada dia a les 2:30 AM
- `IntervalTrigger(hours=24)` → Cada 24 hores des de l'última execució

### Pickle
Serialitza objectes de Python a fitxers binaris:
```python
# Guardar
pickle.dump(model_data, file)

# Carregar
model_data = pickle.load(file)
```

## 📝 Crèdits

Projecte acadèmic de sistema de recomanacions d'animes amb:
- Flask (API REST)
- Pandas + NumPy (Data processing)
- APScheduler (Tasques automàtiques)
- Collaborative Filtering (Pearson correlation)

---

**Made with ❤️ i molt de temps esperant que s'entreni el model 😅**
