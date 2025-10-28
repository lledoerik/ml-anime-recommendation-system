// Sistema de rating amb estrelles
const stars = document.querySelectorAll('.star');
const ratingValue = document.getElementById('ratingValue');
const ratingInput = document.getElementById('ratingInput');
let currentRating = 0;

stars.forEach((star, index) => {
    // Click per seleccionar rating
    star.addEventListener('click', (e) => {
        const rect = star.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const starWidth = rect.width;
        const starNumber = index + 1;

        // Si es clica a la meitat esquerra, puntua .5, si no puntua enter
        if (clickX < starWidth / 2) {
            currentRating = starNumber - 0.5;
        } else {
            currentRating = starNumber;
        }

        updateRating(currentRating);
    });

    // Hover per preview
    star.addEventListener('mousemove', (e) => {
        const rect = star.getBoundingClientRect();
        const hoverX = e.clientX - rect.left;
        const starWidth = rect.width;
        const starNumber = index + 1;

        let previewRating;
        if (hoverX < starWidth / 2) {
            previewRating = starNumber - 0.5;
        } else {
            previewRating = starNumber;
        }

        highlightStars(previewRating);
    });
});

document.getElementById('starRating').addEventListener('mouseleave', () => {
    highlightStars(currentRating);
});

function updateRating(rating) {
    currentRating = rating;
    ratingInput.value = rating;
    ratingValue.textContent = `${rating}/5`;
    highlightStars(rating);
}

function highlightStars(rating) {
    stars.forEach((star, index) => {
        const starNumber = index + 1;

        star.classList.remove('full', 'half');

        if (rating >= starNumber) {
            // Estrella completa
            star.classList.add('full');
        } else if (rating >= starNumber - 0.5) {
            // Mitja estrella
            star.classList.add('half');
        }
    });
}

// Gestió del formulari
const form = document.getElementById('recommendForm');
const resultsSection = document.getElementById('resultsSection');
const animeGrid = document.getElementById('animeGrid');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsCount = document.getElementById('resultsCount');

// URL de la API (canvia-la si és necessari)
const API_URL = 'http://localhost:5000';

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const animeName = document.getElementById('animeSearch').value;
    const rating = currentRating;

    if (rating === 0) {
        alert('Si us plau, selecciona una valoració!');
        return;
    }

    // Mostrar secció de resultats i loading
    resultsSection.classList.remove('hidden');
    loadingIndicator.classList.remove('hidden');
    animeGrid.innerHTML = '';

    // Scroll suau fins als resultats
    resultsSection.scrollIntoView({behavior: 'smooth'});

    try {
        // Crida a l'API de Flask
        const response = await fetch(`${API_URL}/api/recommendations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                anime: animeName,
                rating: rating
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error en obtenir recomanacions');
        }

        const data = await response.json();
        displayResults(data.recommendations, animeName, rating);

    } catch (error) {
        console.error('Error:', error);
        loadingIndicator.classList.add('hidden');

        let errorMessage = 'Error en obtenir les recomanacions.';

        if (error.message.includes("No s'ha trobat")) {
            errorMessage = `No s'ha trobat l'anime "${animeName}". Si us plau, prova amb un altre nom.`;
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'No es pot connectar amb el servidor. Assegura\'t que l\'API Flask està en funcionament.';
        } else {
            errorMessage = error.message;
        }

        animeGrid.innerHTML = `<div class="error-message">${errorMessage}</div>`;
    }
});

function displayResults(recommendations, animeName, rating) {
    loadingIndicator.classList.add('hidden');
    animeGrid.innerHTML = '';

    if (!recommendations || recommendations.length === 0) {
        animeGrid.innerHTML = '<div class="error-message">No s\'han trobat recomanacions.</div>';
        return;
    }

    resultsCount.textContent = `${recommendations.length} animes recomanats basats en "${animeName}" (valoració: ${rating}/5)`;

    recommendations.forEach(anime => {
        const card = createAnimeCard(anime);
        animeGrid.appendChild(card);
    });
}

function createAnimeCard(anime) {
    const card = document.createElement('div');
    card.className = 'anime-card';

    // Calcular color de correlació
    const correlationPercent = anime.correlation * 100;
    let correlationColor = '#10b981'; // verd
    if (correlationPercent < 50) {
        correlationColor = '#ef4444'; // vermell
    } else if (correlationPercent < 70) {
        correlationColor = '#f59e0b'; // taronja
    }

    card.innerHTML = `
        <div class="anime-title">${anime.title}</div>
        <div class="anime-info">
            <div class="anime-score">
                ★ ${anime.score}
            </div>
            ${anime.genre ? `<div>Gènere: ${anime.genre}</div>` : ''}
            ${anime.year ? `<div>Any: ${anime.year}</div>` : ''}
            ${anime.correlation !== undefined ? 
                `<div style="color: ${correlationColor}; font-weight: 600;">
                    Similitud: ${(anime.correlation * 100).toFixed(0)}%
                </div>` : ''}
        </div>
    `;

    return card;
}

// Funció per carregar tots els animes disponibles (opcional)
async function loadAvailableAnimes() {
    try {
        const response = await fetch(`${API_URL}/api/animes`);
        const data = await response.json();
        return data.animes;
    } catch (error) {
        console.error('Error carregant animes:', error);
        return [];
    }
}

// Autocompletat

const animeSearchInput = document.getElementById('animeSearch');
let availableAnimes = [];

loadAvailableAnimes().then(animes => {
    availableAnimes = animes;
});

animeSearchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    if (query.length > 2) {
        const suggestions = availableAnimes.filter(anime =>
            anime.name.toLowerCase().includes(query)
        ).slice(0, 5);
        // Aquí pots mostrar les suggerències
        console.log('Suggerències:', suggestions);
    }
});
