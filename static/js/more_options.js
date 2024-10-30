// Menu templates for different item types
const MENU_TEMPLATES = {
    queue: {
        id: 'options-menu-queue',
        items: [
            { action: 'remove_song', icon: 'trash', text: 'Remove' },
            { action: 'radio_song', icon: 'radio', text: 'Radio' },
            { action: 'play_next', icon: 'play-next', text: 'Play next' },
            { action: 'play_end', icon: 'play-end', text: 'End of queue' },
            { action: 'Search_radio', icon: 'music-note', text: 'Search radio' },
            { action: 'Search_artist', icon: 'user', text: 'Search artist' },
            { action: 'Search_album', icon: 'album', text: 'Search album' },
            { action: 'yeet_queue', icon: 'fire', text: 'Yeet queue' }
        ]
    },
    song: {
        id: 'options-menu-song',
        items: [
            { action: 'radio_song', icon: 'radio', text: 'Radio' },
            { action: 'play_next', icon: 'play-next', text: 'Play next' },
            { action: 'play_end', icon: 'play-end', text: 'End of queue' },
            { action: 'Search_radio', icon: 'music-note', text: 'Search radio' },
            { action: 'Search_artist', icon: 'user', text: 'Search artist' },
            { action: 'Search_album', icon: 'album', text: 'Search album' }
        ]
    },
    albums: {
        id: 'options-menu-album',
        items: [
            { action: 'open_album', icon: 'external-link', text: 'Open' },
            { action: 'play_next', icon: 'play-next', text: 'Play all next' },
            { action: 'play_end', icon: 'play-end', text: 'Add all to queue' },
            { action: 'Search_artist', icon: 'user', text: 'Search artist' }
        ]
    },
    playlists: {
        id: 'options-menu-album',
        items: [
            { action: 'open_playlist', icon: 'external-link', text: 'Open' },
            { action: 'play_next', icon: 'play-next', text: 'Play all next' },
            { action: 'play_end', icon: 'play-end', text: 'Add all to queue' },
            { action: 'Search_artist', icon: 'user', text: 'Search artist' }
        ]
    },
    artists: {
        id: 'options-menu-album',
        items: [
            { action: 'open_artist', icon: 'external-link', text: 'Open' },
            { action: 'play_end', icon: 'play-end', text: 'Add all to radio queue' },
            { action: 'search_album_artist', icon: 'album', text: 'Search album' }
        ]
    }
};

// SVG icon mapping
const ICONS = {
    'trash': '<path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />',
    // Add other icon paths here...
};

const song_container = document.getElementById('song-container');

// Helper function to create menu HTML
function createMenuHTML(template, uuid) {
    const menuItems = template.items.map(item => `
        <li onclick="${item.action}('${uuid}')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                ${ICONS[item.icon]}
            </svg>
            ${item.text}
        </li>
    `).join('');

    return `
        <div id="${template.id}" class="options-menu">
            <ul class="bg-primary">${menuItems}</ul>
            <input id="more_uuid" type="hidden" name="uuid" value="${uuid}">
        </div>
    `;
}

// Main more_options function
function more_options(event, item, item_type) {
    event.preventDefault();
    rippler(event);

    // Remove existing menu
    const openMenu = document.querySelector('.options-menu');
    if (openMenu) openMenu.remove();

    // Create new menu
    const template = MENU_TEMPLATES[item_type] || MENU_TEMPLATES.song;
    const menuHTML = createMenuHTML(template, item);
    const menu = new DOMParser().parseFromString(menuHTML, 'text/html').body.firstChild;

    // Position menu
    positionMenu(menu, event);

    // Add menu to document
    document.body.appendChild(menu);
    htmx.process(menu);
}

// Helper function to position menu
function positionMenu(menu, event) {
    const x = event.button === 2 ? event.clientX : event.currentTarget.getBoundingClientRect().left;
    const y = event.button === 2 ? event.clientY : event.currentTarget.getBoundingClientRect().bottom;

    menu.style.visibility = 'hidden';
    document.body.appendChild(menu);

    const rect = menu.getBoundingClientRect();
    const adjustedX = Math.min(Math.max(0, x), window.innerWidth - rect.width);
    const adjustedY = Math.min(Math.max(0, y), window.innerHeight - rect.height);

    menu.style.left = `${adjustedX}px`;
    menu.style.top = `${adjustedY}px`;
    menu.style.visibility = 'visible';
}

// API functions
const api = {
    async post(endpoint, data) {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(data)
        });
        return response;
    },

    async updateContainer(endpoint, data) {
        const response = await this.post(endpoint, data);
        if (!response.ok) throw new Error(response.statusText);
        const html = await response.text();
        song_container.innerHTML = html;
        htmx.process(song_container);
    }
};

// Action functions
function get_song(uuid) {
    return song_dict[uuid] || JSON.parse(document.getElementById(`search-song-${uuid}`)?.value);
}

async function radio_song(uuid) {
    const song = get_song(uuid);
    await api.post('/radio', { videoId: song?.videoId || uuid });
}

async function play_next(uuid) {
    const song = get_song(uuid);
    await api.post('/play_next', { song: JSON.stringify(song) });
}

async function play_end(uuid) {
    const song = get_song(uuid);
    await api.post('/add_to_queue', { song: JSON.stringify(song) });
}

async function remove_song(uuid) {
    const song = get_song(uuid);
    await api.post('/remove', { uuid: JSON.stringify(song.uuid) });
}

// Event listeners
document.addEventListener('click', () => {
    document.querySelector('.options-menu')?.remove();
});

document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        document.querySelector('.options-menu')?.remove();
    }
});

// Export functions
window.more_options = more_options;
window.radio_song = radio_song;
window.play_next = play_next;
window.play_end = play_end;
window.remove_song = remove_song;
// Export other functions as needed...