let selectedIndex = -1; // To track the currently selected suggestion

function showSuggestions(value) {
    if (value.length === 0) {
        document.getElementById('suggestions-container').classList.add('hidden');
        return;
    }
    socket.emit('search_suggestions', { q: value });
}

function processSearchSugestions(data) {
    const suggestionsContainer = document.getElementById('suggestions-container');
    suggestionsContainer.innerHTML = '';
    selectedIndex = -1; // Reset the selected index

    data.forEach((suggestion, index) => {
        // Create a div for each suggestion
        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'p-2 cursor-pointer hover:bg-zinc-700';
        suggestionDiv.dataset.index = index; // Store the index for keyboard navigation

        // Create a span to hold the formatted suggestion text
        const suggestionText = document.createElement('span');

        // Process the "runs" to format text
        suggestion.runs.forEach(run => {
            const textNode = document.createElement('span');
            textNode.textContent = run.text;
            if (run.bold) {
                textNode.style.fontWeight = 'bold';
            }
            suggestionText.appendChild(textNode);
        });

        // Append the formatted text to the suggestion div
        suggestionDiv.appendChild(suggestionText);

        // Add mousedown event to select suggestion
        suggestionDiv.onmousedown = (event) => {
            event.preventDefault(); // Prevents default behavior and keeps the menu open
            document.getElementById('search_input').value = suggestion.text;
            document.getElementById('search_img').click(); // Trigger search or any other action
        };

        // Append suggestion div to the container
        suggestionsContainer.appendChild(suggestionDiv);
    });

    // Show the suggestions container if there are suggestions
    if (data.length > 0) {
        suggestionsContainer.classList.remove('hidden');
    } else {
        suggestionsContainer.classList.add('hidden');
    }
}

// Handle keyboard navigation
function handleKeyboardNavigation(event) {
    const suggestionsContainer = document.getElementById('suggestions-container');
    const suggestions = suggestionsContainer.querySelectorAll('div');
    if (suggestions.length === 0) return;

    if (event.key === 'ArrowDown') {
        event.preventDefault();
        if (selectedIndex < suggestions.length - 1) {
            selectedIndex++;
        }
        highlightSuggestion();
    } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        if (selectedIndex > -1) {
            selectedIndex--;
        }
        highlightSuggestion();
    } else if (event.key === 'Enter') {
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
            event.preventDefault();
            document.getElementById('search_input').value = suggestions[selectedIndex].textContent;
        }
        hideSuggestions();
    }
}

function highlightSuggestion() {
    const suggestionsContainer = document.getElementById('suggestions-container');
    const suggestions = suggestionsContainer.querySelectorAll('div');

    suggestions.forEach((suggestion, index) => {
        if (index === selectedIndex) {
            suggestion.classList.add('bg-zinc-700'); // Highlight the selected suggestion
        } else {
            suggestion.classList.remove('bg-zinc-700'); // Remove highlight from non-selected suggestions
        }
    });
}

// Add event listener for keyboard navigation
document.getElementById('search_input').addEventListener('keydown', handleKeyboardNavigation);

// Add event listener to hide suggestions when clicking outside
document.addEventListener('click', function(event) {
    const suggestionsContainer = document.getElementById('suggestions-container');
    const searchInput = document.getElementById('search_input');
    if (!suggestionsContainer.contains(event.target) && event.target !== searchInput) {
        suggestionsContainer.classList.add('hidden');
    }
});

function hideSuggestions() {
    setTimeout(() => {
        document.getElementById('suggestions-container').classList.add('hidden');
    }, 100);
}