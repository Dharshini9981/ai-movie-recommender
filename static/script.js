// Load dropdown options when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadOptions();
});

// Fetch and populate dropdown options
async function loadOptions() {
    try {
        const response = await fetch('/options');
        const options = await response.json();
        
        // Populate each dropdown
        populateDropdown('genre', options.genres);
        populateDropdown('mood', options.moods);
        populateDropdown('duration', options.durations);
        populateDropdown('content_type', options.content_types);
        populateDropdown('language', options.languages);
    } catch (error) {
        console.error('Error loading options:', error);
    }
}

// Populate a dropdown with options
function populateDropdown(id, options) {
    const select = document.getElementById(id);
    options.forEach(option => {
        const optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        optionElement.setAttribute('data-testid', `${id}-option-${option.toLowerCase()}`);
        select.appendChild(optionElement);
    });
}

// Handle form submission
document.getElementById('recommendForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Get form values
    const formData = {
        genre: document.getElementById('genre').value,
        mood: document.getElementById('mood').value,
        duration: document.getElementById('duration').value,
        content_type: document.getElementById('content_type').value,
        language: document.getElementById('language').value
    };
    
    // Hide form and results, show loading
    document.querySelector('.form-card').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    
    try {
        // Send request to backend
        const response = await fetch('/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data.recommendations);
        } else {
            alert('Error: ' + (data.error || 'Failed to get recommendations'));
            resetToForm();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
        resetToForm();
    }
});

// Display recommendations
function displayRecommendations(recommendations) {
    // Hide loading
    document.getElementById('loading').classList.add('hidden');
    
    // Display top recommendation
    const topRec = recommendations[0];
    document.getElementById('topTitle').textContent = topRec.title;
    document.getElementById('topConfidence').textContent = `${topRec.confidence}% Match`;
    document.getElementById('topExplanation').textContent = topRec.explanation;
    
    // Create detail tags for top recommendation
    const detailsContainer = document.getElementById('topDetails');
    detailsContainer.innerHTML = '';
    
    const details = [
        { label: 'Genre', value: topRec.genre },
        { label: 'Mood', value: topRec.mood },
        { label: 'Type', value: topRec.content_type },
        { label: 'Duration', value: topRec.duration },
        { label: 'Language', value: topRec.language }
    ];
    
    details.forEach(detail => {
        const tag = document.createElement('span');
        tag.className = 'detail-tag';
        tag.textContent = `${detail.label}: ${detail.value}`;
        tag.setAttribute('data-testid', `top-detail-${detail.label.toLowerCase()}`);
        detailsContainer.appendChild(tag);
    });
    
    // Display alternative recommendations
    const alternativesGrid = document.getElementById('alternativesGrid');
    alternativesGrid.innerHTML = '';
    
    for (let i = 1; i < recommendations.length; i++) {
        const rec = recommendations[i];
        const card = createAlternativeCard(rec, i);
        alternativesGrid.appendChild(card);
    }
    
    // Show results
    document.getElementById('results').classList.remove('hidden');
}

// Create alternative recommendation card
function createAlternativeCard(rec, index) {
    const card = document.createElement('div');
    card.className = 'alt-card';
    card.setAttribute('data-testid', `alternative-card-${index}`);
    
    card.innerHTML = `
        <h4 class="alt-title" data-testid="alt-title-${index}">${rec.title}</h4>
        <div class="alt-confidence" data-testid="alt-confidence-${index}">${rec.confidence}% Match</div>
        <div class="alt-details">
            <div class="alt-detail" data-testid="alt-genre-${index}">📽️ ${rec.genre}</div>
            <div class="alt-detail" data-testid="alt-mood-${index}">😊 ${rec.mood}</div>
            <div class="alt-detail" data-testid="alt-type-${index}">🎬 ${rec.content_type}</div>
            <div class="alt-detail" data-testid="alt-language-${index}">🌐 ${rec.language}</div>
        </div>
    `;
    
    return card;
}

// Reset to form view
function resetToForm() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('results').classList.add('hidden');
    document.querySelector('.form-card').classList.remove('hidden');
}

// Handle reset button
document.getElementById('resetBtn').addEventListener('click', function() {
    document.getElementById('recommendForm').reset();
    resetToForm();
});