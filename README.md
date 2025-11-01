# 🎬 Sistema de Recomanacions d'Animes v2.0

Sistema intel·ligent de recomanacions basat en collaborative filtering amb correlació de Pearson. Ara amb suport per valoracions negatives, selecció múltiple d'animes, i reload automàtic de models!

## 🚀 Novetats v2.0

### ✨ Noves Funcionalitats

✅ **Recomanacions ajustades segons valoració:**
   - ⭐ **Alta (4-5)**: Troba animes similars
   - 😐 **Mitjana (3)**: Animes moderadament relacionats  
   - 👎 **Baixa (1-2)**: Descobreix alternatives diferents

✅ **Selector múltiple d'animes:** Quan hi ha diversos animes amb el mateix nom, pots triar el correcte

✅ **Reload automàtic de models:** Detecta i carrega models nous cada 30 segons sense reiniciar

✅ **Millor suport UTF-8:** Mostra correctament noms japonesos i caràcters especials

✅ **API compatible amb producció:** Funciona tant en localhost com a recomanador.hermes.cat

## 📋 Característiques

- **Recomanacions intel·ligents** amb correlació de Pearson ajustada
- **Entrenament automàtic** cada dia a les 2:30 AM
- **Sistema de versionat** de models (v1, v2, v3...)
- **Footer informatiu** amb versió del model en temps real
- **Càrrega ràpida** (2-3 segons vs 20 minuts!)
- **Entrenament en background** sense bloquejar
- **API REST** completa amb Flask
- **Interfície web** moderna i responsive

## 🔧 Instal·lació

### 1. Requisits
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Entrenar el Model (OBLIGATORI la primera vegada)
```bash
python scripts/train_model.py
```

⏱️ **Temps estimat:** 5-10 minuts segons la mida del dataset

### 3. Executar l'Aplicació
```bash
python app.py
```

Accedeix a:
- Local: `http://localhost:5000`
- Producció: `https://recomanador.hermes.cat`

## 🤖 Com Funciona el Sistema

### Sistema de Valoracions

El sistema ara interpreta les valoracions de manera intel·ligent:

| Valoració | Comportament | Exemple |
|-----------|--------------|---------|
| ⭐⭐⭐⭐⭐ (4-5) | Cerca animes similars | Si t'agrada "Death Note", et recomana thrillers psicològics |
| ⭐⭐⭐ (3) | Cerca animes moderats | Recomanacions neutrals, ni molt similars ni molt diferents |
| ⭐⭐ (1-2) | Cerca alternatives | Si no t'agrada "One Piece", et recomana animes curts o d'altres gèneres |

### Reload Automàtic de Models

L'aplicació comprova cada **30 segons** si hi ha models nous:
- Si entrenes manualment amb `train_model.py`, es detecta automàticament
- No cal reiniciar l'API
- Els usuaris no noten cap interrupció

### Múltiples Coincidències

Si cerques "Detective Conan" i hi ha diversos resultats:
1. El sistema mostra tots els animes coincidents
2. Pots seleccionar l'anime exacte que vols
3. Les recomanacions es basen en la teva selecció específica

## 🌐 API Endpoints

### Recomanacions Principals
```bash
POST /api/recommendations
{
  "anime": "Death Note",
  "rating": 4.5
}

# Resposta amb múltiples coincidències (HTTP 300):
{
  "status": "multiple_matches",
  "matches": [
    {"name": "Death Note", "genre": "Thriller"},
    {"name": "Death Note: Rewrite", "genre": "Recap"}
  ]
}
```

### Informació del Model
```bash
GET /api/model-info

{
  "version": 3,
  "loaded_at": "2025-10-31T12:30:45",
  "num_animes": 12294,
  "num_users": 73516,
  "training_in_progress": false
}
```

## 🛠️ Resolució de Problemes

### Les recomanacions no semblen bones

**Possibles causes:**
1. **Dataset massa petit**: El fitxer `rating_balanceado.csv` té massa filtres
2. **Pocs usuaris en comú**: Baixa el `min_periods` a la correlació (ara està a 50)

**Solució:**
```python
# A recommendation_system.py, canvia:
self.corrMatrix = self.userRatings_pivot.corr(method='pearson', min_periods=30)  # Baixar més
```

### Caràcters japonesos no es veuen bé

**Solució implementada:**
- Tots els CSV es llegeixen amb `encoding='utf-8'`
- HTML té `<meta charset="UTF-8">`
- CSS inclou fonts japoneses

Si encara tens problemes, converteix els CSV:
```bash
iconv -f ISO-8859-1 -t UTF-8 data/anime.csv > data/anime_utf8.csv
mv data/anime_utf8.csv data/anime.csv
```

### Error de connexió a l'API

**Per producció:**
- L'app SEMPRE ha d'executar-se amb `host='0.0.0.0'`
- El domini `recomanador.hermes.cat` ha d'apuntar al servidor
- El JavaScript utilitza `window.location.origin` per trobar l'API

### L'entrenament automàtic no funciona

Verifica que:
1. El scheduler està actiu (mira els logs)
2. Els fitxers CSV han canviat realment
3. No hi ha un entrenament ja en curs

## 📊 Millores del Model

### Per millorar la qualitat de les recomanacions:

1. **Augmentar el dataset:**
   - Usa `rating.csv` original amb menys filtres
   - O baixa els llindars a `data_cleaner.py`

2. **Ajustar paràmetres:**
   ```python
   # Mínim d'usuaris per calcular correlació
   min_periods=30  # Baixar per més cobertura
   
   # Mínim de valoracions per anime
   popular_animes = self.animeStats['rating'] >= 30  # Baixar per més varietat
   ```

3. **Afegir més factors:**
   - Gèneres
   - Any de llançament
   - Popularitat global

## 💡 Consells d'Ús

### Per als usuaris:
- **Puntua alt (4-5)** animes que t'agraden per trobar similars
- **Puntua baix (1-2)** animes que no t'agraden per descobrir alternatives
- **Puntua neutral (3)** per explorar moderadament

### Per als desenvolupadors:
- Models nous es detecten automàticament cada 30 segons
- L'entrenament manual no bloqueja l'API
- Pots tenir múltiples versions de models

## 📝 Arquitectura Tècnica

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend   │────▶│   Flask API  │────▶│Recommendation│
│  JavaScript  │     │   (app.py)   │     │    System    │
└──────────────┘     └──────────────┘     └──────────────┘
                            │                      │
                     ┌──────▼──────┐      ┌───────▼──────┐
                     │  Scheduler  │      │ Pickle Models│
                     │ (APScheduler)│      │  (v1,v2,v3) │
                     └──────────────┘      └──────────────┘
```

## 🚀 Roadmap Futur

- [ ] Implementar cache de recomanacions
- [ ] Afegir filtratge per gèneres
- [ ] Sistema de login i perfils d'usuari
- [ ] Històric de recomanacions
- [ ] Exportar/importar models
- [ ] Integració amb APIs externes (MyAnimeList, etc.)

---

**Desenvolupat amb ❤️ per la comunitat anime**

*Versió 2.0 - Octubre 2025*
