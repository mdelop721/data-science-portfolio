document.addEventListener('DOMContentLoaded', () => {
    const langButtons = document.querySelectorAll('.lang-switcher button');
    const translatableElements = document.querySelectorAll('[data-es]');

    const setLanguage = (lang) => {
        console.log('Switching language to:', lang);
        translatableElements.forEach(el => {
            const translation = el.getAttribute(`data-${lang}`);
            if (translation) {
                // If the element has children (like <span> in h1), we need to be careful with innerHTML vs textContent
                if (el.tagName === 'A' || el.tagName === 'P' || el.tagName === 'SPAN' || el.tagName === 'H2' || el.tagName === 'H3' || el.tagName === 'BUTTON') {
                    el.innerHTML = translation;
                } else if (el.tagName === 'H1') {
                    el.innerHTML = translation;
                } else {
                    el.textContent = translation;
                }
            }
        });

        // Update active button state
        langButtons.forEach(btn => {
            btn.classList.remove('active');
            if (btn.id === `lang-${lang}`) {
                btn.classList.add('active');
            }
        });

        // Store preference
        localStorage.setItem('preferredLang', lang);
    };

    langButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.id.replace('lang-', '');
            setLanguage(lang);
        });
    });

    // Check for stored preference or default to ES
    const savedLang = localStorage.getItem('preferredLang') || 'es';
    setLanguage(savedLang);
});
