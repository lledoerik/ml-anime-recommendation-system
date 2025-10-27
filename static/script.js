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
    ratingValue.textContent = `${rating}/10`;
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
        // AQUÍ HAS DE CRIDAR A LA TEVA API DE FLASK
        // Exemple de crida fetch:
        /*
        const response = await fetch('/api/recommendations', {
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
            throw new Error('Error en obtenir recomanacions');
        }

        const data = await response.json();
        displayResults(data.recommendations);
        */

        // DADES DE PROVA
        setTimeout(() => {
            const mockData = generateMockRecommendations(animeName, rating);
            displayResults(mockData);
        }, 1500);

    } catch (error) {
        console.error('Error:', error);
        loadingIndicator.classList.add('hidden');
        animeGrid.innerHTML = '<div class="error-message">Error en obtenir les recomanacions. Si us plau, torna-ho a intentar.</div>';
    }
});

function displayResults(recommendations) {
    loadingIndicator.classList.add('hidden');
    animeGrid.innerHTML = '';

    resultsCount.textContent = `${recommendations.length} animes trobats`;

    recommendations.forEach(anime => {
        const card = createAnimeCard(anime);
        animeGrid.appendChild(card);
    });
}

function createAnimeCard(anime) {
    const card = document.createElement('div');
    card.className = 'anime-card';

    card.innerHTML = `
                <div class="anime-title">${anime.title}</div>
                <div class="anime-info">
                    <div class="anime-score">
                        ★ ${anime.score.toFixed(1)}
                    </div>
                    ${anime.genre ? `<div>Gènere: ${anime.genre}</div>` : ''}
                    ${anime.year ? `<div>Any: ${anime.year}</div>` : ''}
                    ${anime.correlation ? `<div>Correlació: ${(anime.correlation * 100).toFixed(0)}%</div>` : ''}
                </div>
            `;

    return card;
}

// FUNCIÓ DE DADES DE PROVA
function generateMockRecommendations(searchTerm, rating) {
    const mockAnimes = [
        {title: 'Steins;Gate', score: 9.1, genre: 'Sci-Fi, Thriller', year: 2011, correlation: 0.89},
        {title: 'Psycho-Pass', score: 8.7, genre: 'Thriller, Sci-Fi', year: 2012, correlation: 0.85},
        {title: 'Elfen Lied', score: 7.8, genre: 'Horror, Action', year: 2014, correlation: 0.72},
        {title: 'Monster', score: 8.9, genre: 'Mystery, Drama', year: 2004, correlation: 0.80},
        {title: 'Parasyte', score: 8.3, genre: 'Horror, Sci-Fi', year: 2014, correlation: 0.78},
        {title: 'Erased', score: 8.5, genre: 'Mystery, Thriller', year: 2016, correlation: 0.75},
    ];

    return mockAnimes.slice(0, 6);
}