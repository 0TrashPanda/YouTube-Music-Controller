const optionsMenuTemplate = document.getElementById('options-menu-template');

function more_options(event, icon, x = null, y = null) {
    rippler(event);
    // If a menu is already open, close it
    if (optionsMenuTemplate.style.visibility === 'visible') {
        optionsMenuTemplate.style.visibility = 'hidden';
    }

    // Clone the menu template and append it to the document body
    let menu = optionsMenuTemplate;

    // Set the song UUID in the menu form
    const uuid = icon.parentElement.parentElement.querySelector('input[name="uuid"]').value;
    menu.querySelector('input[name="uuid"]').value = uuid;

    // Calculate the default position based on the clicked icon
    const rect = icon.getBoundingClientRect();
    let top = y !== null ? y : rect.bottom + window.scrollY;
    let left = x !== null ? x : rect.left + window.scrollX;

    // Adjust the position if the menu overflows the viewport
    const menu_width = menu.offsetWidth;
    if (left + menu_width > window.innerWidth) {
        // Align the menu to the right side of the icon
        left = rect.right - menu_width + window.scrollX;
    }
    if (left < 0) {
        left = 0;
    }
    const menu_bottom = top + menu.offsetHeight;
    if (menu_bottom > window.innerHeight) {
        top = window.innerHeight - menu.offsetHeight;
    }

    // Apply the calculated or overridden position to the menu
    menu.style.top = `${top}px`;
    menu.style.left = `${left}px`;
    menu.style.visibility = 'visible';

    // Reprocess the menu to ensure it updates with HTMX
    htmx.process(menu);

    // Stop event propagation
    event.stopPropagation();
}

function more_options_rc(event, icon) {
    event.preventDefault();
    more_options(event, icon.querySelector('svg'), event.clientX, event.clientY);
}

// Close the menu when clicking outside of it
document.addEventListener('click', function () {
    optionsMenuTemplate.style.visibility = 'hidden';
});

function get_song(uuid) {
    let song = song_dict[uuid];
    return song;
}

function radio_song(uuid) {
    console.log(uuid);
    let song = get_song(uuid);
    videoId = song.videoId;
    console.log(song);
    console.log(videoId);
    // post request to /radio with videoId
    // @app.route('/radio', methods=['POST'])
    // def radio():
    //     videoId = request.form.get('videoId')

    fetch('/radio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'videoId': videoId
        })
    })
}

function play_next(uuid) {
    let song = get_song(uuid);
    fetch('/play_next', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'song': JSON.stringify(song)
        })
    })
}

function rippler(e) {
    const button = e.currentTarget;
    // Create a span element for the ripple
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');

    // Get the size of the button and position of the cursor
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = `${size}px`;

    const x = e.clientX - rect.left - window.scrollX - size / 2;
    const y = e.clientY - rect.top - window.scrollY - size / 2;

    // Set the position of the ripple
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;

    // Append the ripple to the button
    button.appendChild(ripple);

    // Remove the ripple after the animation is done
    ripple.addEventListener('animationend', () => {
        ripple.remove();
    });
}