// Make sure this is at the top, outside of any functions
const sections = {
    search: document.getElementById('search'),
    player: document.getElementById('player'),
    queues: document.getElementById('queues'),
};
function scrollToPanel(panelId) {
    if (sections[panelId]) {
        sections[panelId].scrollIntoView({ behavior: 'smooth' });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const sections = {
        search: document.getElementById('search'),
        player: document.getElementById('player'),
        queues: document.getElementById('queues'),
    };

    const navButtons = {
        search: document.getElementById('nav_search').getElementsByTagName('svg')[0],
        player: document.getElementById('nav_player').getElementsByTagName('svg')[0],
        queues: document.getElementById('nav_queues').getElementsByTagName('svg')[0],
    };

    function setActiveNav(panelId) {
        // Remove active class from all buttons
        for (let key in navButtons) {
            if (navButtons[key]) {
                navButtons[key].classList.remove('nav_icon_active');
            }
        }
        // Add active class to the correct button
        if (navButtons[panelId]) {
            navButtons[panelId].classList.add('nav_icon_active');
        }
    }

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setActiveNav(entry.target.id);
            }
        });
    }, {
        threshold: 0.5  // Adjust this value to determine when a section is considered "in view"
    });

    // Observe each section
    for (let key in sections) {
        if (sections[key]) {
            observer.observe(sections[key]);
        }
    }
});
