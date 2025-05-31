// Variables globales
let allArticles = [];
let filteredArticles = [];
let autoUpdateEnabled = false;
let updateInterval;

// Initialisation quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM chargé, initialisation...');
    initializeApp();
});

function initializeApp() {
    // Charger les articles depuis les données
    loadArticles();
    
    // Configurer les événements
    setupEventListeners();
    
    // Afficher tous les articles initialement
    displayArticles();
    
    // Mettre à jour le compteur
    updateResultCount();
    
    console.log(`${allArticles.length} articles chargés`);
}

function loadArticles() {
    // Utiliser les données du fichier articles-data.js
    if (window.articlesData) {
        allArticles = [...window.articlesData];
        filteredArticles = [...allArticles];
        console.log('Articles chargés depuis articles-data.js');
    } else {
        console.error('Données des articles non trouvées');
    }
}

function setupEventListeners() {
    // Recherche en temps réel
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
        console.log('Event listener ajouté pour la recherche');
    }
    
    // Filtre par année
    const yearFilter = document.getElementById('yearFilter');
    if (yearFilter) {
        yearFilter.addEventListener('change', handleYearFilter);
    }
    
    // Boutons
    const showTop10 = document.getElementById('showTop10');
    if (showTop10) {
        showTop10.addEventListener('click', showTop10Articles);
    }
    
    const showAll = document.getElementById('showAll');
    if (showAll) {
        showAll.addEventListener('click', showAllArticles);
    }
    
    // Auto-update (optionnel)
    const toggleAutoUpdate = document.getElementById('toggleAutoUpdate');
    if (toggleAutoUpdate) {
        toggleAutoUpdate.addEventListener('click', toggleAutoUpdateFunction);
    }
    
    const manualUpdate = document.getElementById('manualUpdate');
    if (manualUpdate) {
        manualUpdate.addEventListener('click', manualUpdateFunction);
    }
    
    const intervalSelect = document.getElementById('intervalSelect');
    if (intervalSelect) {
        intervalSelect.addEventListener('change', updateIntervalSetting);
    }
}

function handleSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const yearFilter = document.getElementById('yearFilter').value;
    
    console.log('Recherche:', searchTerm, 'Année:', yearFilter);
    
    filteredArticles = allArticles.filter(article => {
        // Vérifier correspondance avec le terme de recherche
        const matchesSearch = searchTerm === '' || 
            article.title.toLowerCase().includes(searchTerm) ||
            article.authors.toLowerCase().includes(searchTerm) ||
            article.date.includes(searchTerm);
        
        // Vérifier correspondance avec l'année
        const matchesYear = yearFilter === '' || article.date.startsWith(yearFilter);
        
        return matchesSearch && matchesYear;
    });
    
    console.log(`${filteredArticles.length} articles trouvés`);
    
    displayArticles();
    updateResultCount();
}

function handleYearFilter() {
    handleSearch(); // Réutilise la logique de recherche
}

function displayArticles() {
    const tbody = document.getElementById('articlesBody');
    const noResults = document.getElementById('noResults');
    const table = document.getElementById('articlesTable');
    
    if (!tbody) {
        console.error('Élément tbody non trouvé');
        return;
    }
    
    // Vider le tableau
    tbody.innerHTML = '';
    
    if (filteredArticles.length === 0) {
        // Afficher le message "aucun résultat"
        if (noResults) noResults.style.display = 'block';
        if (table) table.style.display = 'none';
    } else {
        // Masquer le message "aucun résultat"
        if (noResults) noResults.style.display = 'none';
        if (table) table.style.display = 'table';
        
        const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
        
        // Créer les lignes du tableau
        filteredArticles.forEach(article => {
            const row = document.createElement('tr');
            
            // Créer les cellules
            const dateCell = document.createElement('td');
            const authorsCell = document.createElement('td');
            const titleCell = document.createElement('td');
            const pdfCell = document.createElement('td');
            
            // Remplir les cellules avec surlignage si nécessaire
            dateCell.innerHTML = highlightText(article.date, searchTerm);
            authorsCell.innerHTML = highlightText(article.authors, searchTerm);
            titleCell.innerHTML = highlightText(article.title, searchTerm);
            pdfCell.innerHTML = article.pdf;
            
            // Ajouter les cellules à la ligne
            row.appendChild(dateCell);
            row.appendChild(authorsCell);
            row.appendChild(titleCell);
            row.appendChild(pdfCell);
            
            tbody.appendChild(row);
        });
    }
}

function highlightText(text, searchTerm) {
    if (!searchTerm || searchTerm.length === 0) return text;
    
    try {
        const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    } catch (error) {
        console.error('Erreur dans highlightText:', error);
        return text;
    }
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function showTop10Articles() {
    filteredArticles = allArticles.slice(0, 10);
    displayArticles();
    updateResultCount();
    
    // Réinitialiser les filtres
    document.getElementById('searchInput').value = '';
    document.getElementById('yearFilter').value = '';
    
    console.log('Affichage des 10 derniers articles');
}

function showAllArticles() {
    filteredArticles = [...allArticles];
    displayArticles();
    updateResultCount();
    
    // Réinitialiser les filtres
    document.getElementById('searchInput').value = '';
    document.getElementById('yearFilter').value = '';
    
    console.log('Affichage de tous les articles');
}

function updateResultCount() {
    const resultCount = document.getElementById('resultCount');
    const articleCount = document.getElementById('articleCount');
    
    if (resultCount) {
        if (filteredArticles.length === allArticles.length) {
            resultCount.textContent = 'Showing all articles';
        } else {
            resultCount.textContent = `Showing ${filteredArticles.length} of ${allArticles.length} articles`;
        }
    }
    
    if (articleCount) {
        articleCount.textContent = allArticles.length;
    }
}

// Fonctions pour l'auto-update (optionnelles)
function toggleAutoUpdateFunction() {
    const button = document.getElementById('toggleAutoUpdate');
    const status = document.getElementById('updateStatus');
    
    if (autoUpdateEnabled) {
        clearInterval(updateInterval);
        autoUpdateEnabled = false;
        if (button) button.textContent = 'Enable Auto-Update';
        const nextUpdate = document.getElementById('nextUpdate');
        if (nextUpdate) nextUpdate.textContent = 'Not scheduled';
        if (status) status.className = 'update-status';
    } else {
        const intervalSelect = document.getElementById('intervalSelect');
        const interval = parseInt(intervalSelect ? intervalSelect.value : 30) * 60000;
        updateInterval = setInterval(manualUpdateFunction, interval);
        autoUpdateEnabled = true;
        if (button) button.textContent = 'Disable Auto-Update';
        updateNextUpdateTime();
        if (status) status.className = 'update-status updating';
    }
}

function updateNextUpdateTime() {
    if (autoUpdateEnabled) {
        const intervalSelect = document.getElementById('intervalSelect');
        const interval = parseInt(intervalSelect ? intervalSelect.value : 30);
        const nextUpdate = new Date(Date.now() + interval * 60000);
        const nextUpdateElement = document.getElementById('nextUpdate');
        if (nextUpdateElement) {
            nextUpdateElement.textContent = nextUpdate.toLocaleTimeString();
        }
    }
}

function updateIntervalSetting() {
    const intervalSelect = document.getElementById('intervalSelect');
    const updateInterval = document.getElementById('updateInterval');
    
    if (intervalSelect && updateInterval) {
        const newInterval = intervalSelect.value;
        updateInterval.textContent = `Every ${newInterval} minutes`;
        
        if (autoUpdateEnabled) {
            toggleAutoUpdateFunction(); // Désactive
            toggleAutoUpdateFunction(); // Réactive avec le nouvel intervalle
        }
    }
}

function manualUpdateFunction() {
    const lastUpdate = document.getElementById('lastUpdate');
    const updateStatus = document.getElementById('updateStatus');
    
    if (lastUpdate) {
        lastUpdate.textContent = new Date().toLocaleString();
    }
    
    if (updateStatus) {
        updateStatus.className = 'update-status';
    }
    
    if (autoUpdateEnabled) {
        updateNextUpdateTime();
    }
    
    console.log('Update completed');
}

// Test pour vérifier que le script fonctionne
console.log('Script search-functionality.js chargé');
