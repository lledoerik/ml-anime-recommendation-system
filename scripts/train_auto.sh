#!/bin/bash

# Script automàtic per entrenar el model d'animes
# Executa: ./scripts/train_auto.sh

echo "======================================================================"
echo "🎬 ENTRENAMENT AUTOMÀTIC DEL MODEL"
echo "======================================================================"
echo ""
echo "Aquest script entrenarà el model de recomanacions automàticament."
echo "El procés pot trigar uns minuts..."
echo ""

# Obtenir el directori del projecte (directori pare del script)
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Canviar al directori del projecte
cd "$PROJECT_DIR" || exit 1

# Executar el script d'entrenament
python scripts/train_model.py

echo ""
echo "======================================================================"
echo "Per executar l'aplicació:"
echo "  python app.py"
echo "======================================================================"
