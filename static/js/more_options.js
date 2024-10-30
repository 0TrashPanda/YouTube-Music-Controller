// Menu templates for different item types
const MENU_TEMPLATES = {
	queue: {
		id: 'options-menu-queue',
		items: [
			{ action: 'remove_song', icon: 'trash', text: 'Remove' },
			{ action: 'radio_song', icon: 'radio', text: 'Radio' },
			{ action: 'play_next', icon: 'play_next', text: 'Play next' },
			{ action: 'play_end', icon: 'play_end', text: 'End of queue' },
			{ action: 'Search_radio', icon: 'music_note', text: 'Search radio' },
			{ action: 'Search_artist', icon: 'user', text: 'Search artist' },
			{ action: 'Search_album', icon: 'album', text: 'Search album' },
			{ action: 'yeet_queue', icon: 'fire', text: 'Yeet queue' }
		],
	},
	song: {
		id: 'options-menu-song',
		items: [
			{ action: 'radio_song', icon: 'radio', text: 'Radio' },
			{ action: 'play_next', icon: 'play_next', text: 'Play next' },
			{ action: 'play_end', icon: 'play_end', text: 'End of queue' },
			{ action: 'Search_radio', icon: 'music_note', text: 'Search radio' },
			{ action: 'Search_artist', icon: 'user', text: 'Search artist' },
			{ action: 'Search_album', icon: 'album', text: 'Search album' },
		],
	},
	albums: {
		id: 'options-menu-album',
		items: [
			{ action: 'open_album', icon: 'external_link', text: 'Open' },
			{ action: 'play_next', icon: 'play_next', text: 'Play all next' },
			{ action: 'play_end', icon: 'play_end', text: 'Add all to queue' },
			{ action: 'Search_artist', icon: 'user', text: 'Search artist' },
		],
	},
	playlists: {
		id: 'options-menu-album',
		items: [
			{ action: 'open_playlist', icon: 'external_link', text: 'Open' },
			{ action: 'play_next', icon: 'play_next', text: 'Play all next' },
			{ action: 'play_end', icon: 'play_end', text: 'Add all to queue' },
			{ action: 'Search_artist', icon: 'user', text: 'Search artist' },
		],
	},
	artists: {
		id: 'options-menu-album',
		items: [
			{ action: 'open_artist', icon: 'external_link', text: 'Open' },
			{ action: 'play_end', icon: 'play_end', text: 'Add all to radio queue' },
			{ action: 'search_album_artist', icon: 'album', text: 'Search album' },
		],
	},
};

// SVG icon mapping
const ICONS = {
	trash: '<path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />',
	radio: '<path stroke-linecap="round" stroke-linejoin="round" d="m3.75 7.5 16.5-4.125M12 6.75c-2.708 0-5.363.224-7.948.655C2.999 7.58 2.25 8.507 2.25 9.574v9.176A2.25 2.25 0 0 0 4.5 21h15a2.25 2.25 0 0 0 2.25-2.25V9.574c0-1.067-.75-1.994-1.802-2.169A48.329 48.329 0 0 0 12 6.75Zm-1.683 6.443-.005.005-.006-.005.006-.005.005.005Zm-.005 2.127-.005-.006.005-.005.005.005-.005.005Zm-2.116-.006-.005.006-.006-.006.005-.005.006.005Zm-.005-2.116-.006-.005.006-.005.005.005-.005.005ZM9.255 10.5v.008h-.008V10.5h.008Zm3.249 1.88-.007.004-.003-.007.006-.003.004.006Zm-1.38 5.126-.003-.006.006-.004.004.007-.006.003Zm.007-6.501-.003.006-.007-.003.004-.007.006.004Zm1.37 5.129-.007-.004.004-.006.006.003-.004.007Zm.504-1.877h-.008v-.007h.008v.007ZM9.255 18v.008h-.008V18h.008Zm-3.246-1.87-.007.004L6 16.127l.006-.003.004.006Zm1.366-5.119-.004-.006.006-.004.004.007-.006.003ZM7.38 17.5l-.003.006-.007-.003.004-.007.006.004Zm-1.376-5.116L6 12.38l.003-.007.007.004-.004.007Zm-.5 1.873h-.008v-.007h.008v.007ZM17.25 12.75a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Zm0 4.5a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Z" />',
	play_next: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h5.25m5.25-.75L17.25 9m0 0L21 12.75M17.25 9v12" />',
	play_end: '<path stroke-linecap="round" stroke-linejoin="round" d="M3 4.5h14.25M3 9h9.75M3 13.5h9.75m4.5-4.5v12m0 0-3.75-3.75M17.25 21 21 17.25" />',
	music_note: '<path stroke-linecap="round" stroke-linejoin="round" d="m9 9 10.5-3m0 6.553v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 1 1-.99-3.467l2.31-.66a2.25 2.25 0 0 0 1.632-2.163Zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0 0 1-1.632 2.163l-1.32.377a1.803 1.803 0 0 1-.99-3.467l2.31-.66A2.25 2.25 0 0 0 9 15.553Z" />',
	user: '<path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />',
	album: '<path stroke-linecap="round" stroke-linejoin="round" d="M20.25 6.375c0 2.278-3.694 4.125-8.25 4.125S3.75 8.653 3.75 6.375m16.5 0c0-2.278-3.694-4.125-8.25-4.125S3.75 4.097 3.75 6.375m16.5 0v11.25c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125V6.375m16.5 0v3.75m-16.5-3.75v3.75m16.5 0v3.75C20.25 16.153 16.556 18 12 18s-8.25-1.847-8.25-4.125v-3.75m16.5 0c0 2.278-3.694 4.125-8.25 4.125s-8.25-1.847-8.25-4.125" />',
	fire: '<path stroke-linecap="round" stroke-linejoin="round" d="M15.362 5.214A8.252 8.252 0 0 1 12 21 8.25 8.25 0 0 1 6.038 7.047 8.287 8.287 0 0 0 9 9.601a8.983 8.983 0 0 1 3.361-6.867 8.21 8.21 0 0 0 3 2.48Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M12 18a3.75 3.75 0 0 0 .495-7.468 5.99 5.99 0 0 0-1.925 3.547 5.975 5.975 0 0 1-2.133-1.001A3.75 3.75 0 0 0 12 18Z" />',
	external_link: '<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />'
};

const song_container = document.getElementById('song-container');

// Helper function to create menu HTML
function createMenuHTML(template, uuid) {
	const menuItems = template.items
		.map(
			(item) => `
        <li onclick="${item.action}('${uuid}')">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                ${ICONS[item.icon]}
            </svg>
            ${item.text}
        </li>
    `
		)
		.join('');

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
	const menu = new DOMParser().parseFromString(menuHTML, 'text/html').body
		.firstChild;

	// Position menu
	positionMenu(menu, event);

	// Add menu to document
	document.body.appendChild(menu);
	htmx.process(menu);
}

// Helper function to position menu
function positionMenu(menu, event) {
	const x =
		event.button === 2
			? event.clientX
			: event.currentTarget.getBoundingClientRect().left;
	const y =
		event.button === 2
			? event.clientY
			: event.currentTarget.getBoundingClientRect().bottom;

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
			body: new URLSearchParams(data),
		});
		return response;
	},

	async updateContainer(endpoint, data) {
		const response = await this.post(endpoint, data);
		if (!response.ok) throw new Error(response.statusText);
		const html = await response.text();
		song_container.innerHTML = html;
		htmx.process(song_container);
	},
};

// Action functions
function get_song(uuid) {
	return (
		song_dict[uuid] ||
		JSON.parse(document.getElementById(`search-song-${uuid}`)?.value)
	);
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

// Add missing functions
function rippler(e) {
	const button = e.currentTarget;
	const ripple = document.createElement('span');
	ripple.classList.add('ripple');

	const rect = button.getBoundingClientRect();
	const size = Math.max(rect.width, rect.height);
	ripple.style.width = ripple.style.height = `${size}px`;

	const x = e.clientX - rect.left - window.scrollX - size / 2;
	const y = e.clientY - rect.top - window.scrollY - size / 2;

	ripple.style.left = `${x}px`;
	ripple.style.top = `${y}px`;
	button.appendChild(ripple);

	ripple.addEventListener('animationend', () => ripple.remove());
}

function search(text) {
	const Search_field = document.getElementById('search_input');
	const search_button = document.getElementById('search_img');
	Search_field.value = text;
	search_button.click();
}

async function Search_radio(uuid) {
	const song = get_song(uuid);
	const videoId = song?.videoId || uuid;
	search(`r/${videoId}`);
}

async function Search_artist(uuid) {
	const song = get_song(uuid);
	if (!song) return;
	search(`a/${song.artists[0]}`);
}

async function Search_album(uuid) {
	const song = get_song(uuid);
	if (!song) return;
	search(`b/${song.album} ${song.artists[0]}`);
}

async function search_album_artist(uuid) {
	const song = get_song(uuid);
	if (!song) return;
	search(`b/${song.title}`);
}

async function open_album(uuid) {
	await api.updateContainer('/open_album', { browseId: uuid });
}

async function open_playlist(uuid) {
	await api.updateContainer('/open_playlist', { browseId: uuid });
}

async function open_artist(uuid) {
	await api.updateContainer('/open_artist', { browseId: uuid });
}

async function yeet_queue(uuid) {
	const song_div = document.querySelector(`input[value='${uuid}']`);
	const queue = song_div.parentElement.parentElement.id;
	const isRadio = queue === 'radio_queue';
	await api.post('/clear_queue', { isRadio: JSON.stringify(isRadio) });
}

// Export all functions to window
window.rippler = rippler;
window.search = search;
window.Search_radio = Search_radio;
window.Search_artist = Search_artist;
window.Search_album = Search_album;
window.search_album_artist = search_album_artist;
window.open_album = open_album;
window.open_playlist = open_playlist;
window.open_artist = open_artist;
window.yeet_queue = yeet_queue;
