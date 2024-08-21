const optionsMenuTemplate = document.getElementById('options-menu-template');

function more_options(event, icon) {
        // If a menu is already open, close it
        if (optionsMenuTemplate.style.visibility === 'visible') {
            optionsMenuTemplate.style.visibility = 'hidden';
        }
        // Clone the menu template and append it to the document body
        // const menu = optionsMenuTemplate.cloneNode(true);
        // menu.id = ''; // Clear the ID to avoid duplicates
        // document.body.appendChild(menu);
        let menu = optionsMenuTemplate

        // Set the song UUID in the menu form
        uuid = icon.parentElement.parentElement.querySelector('input[name="uuid"]').value;
        menu.querySelector('input[name="uuid"]').value = uuid;

        // Position the menu next to the clicked icon
        const rect = icon.getBoundingClientRect();
        menu.style.top = `${rect.bottom + window.scrollY}px`;
        menu.style.left = `${rect.left + window.scrollX}px`;
        menu_width = menu.offsetWidth;
        if (rect.left + menu_width > window.innerWidth) {
            menu.style.left = `${rect.left - menu_width + window.scrollX}px`;
        }
        if (parseInt(menu.style.left) < 0) {
            menu.style.left = `0px`;
        }
        menu_bottom = rect.bottom + menu.offsetHeight;
        if (menu_bottom > window.innerHeight) {
            menu.style.top = `${window.innerHeight - menu.offsetHeight}px`;
        }
        menu.style.visibility = 'visible';

        htmx.process(menu);

        // Stop event propagation
        event.stopPropagation();
}

// Close the menu when clicking outside of it
document.addEventListener('click', function () {
    optionsMenuTemplate.style.visibility = 'hidden';
});
