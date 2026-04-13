document.addEventListener('DOMContentLoaded', () => {
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
            
            // Handle specific attribute translations if they exist
            const hrefContent = el.getAttribute(`data-${lang}-href`);
            if (hrefContent) el.setAttribute('href', hrefContent);
            
            const titleContent = el.getAttribute(`data-${lang}-title`);
            if (titleContent) el.setAttribute('title', titleContent);
            
            const placeholderContent = el.getAttribute(`data-${lang}-placeholder`);
            if (placeholderContent) el.setAttribute('placeholder', placeholderContent);
        });

    // Update toggle state
        const langToggle = document.querySelector('.lang-switcher');
        if (langToggle) {
            const esLabel = langToggle.querySelector('.es-label');
            const enLabel = langToggle.querySelector('.en-label');
            
            if (lang === 'en') {
                langToggle.classList.add('en-active');
                if(enLabel) enLabel.classList.add('active');
                if(esLabel) esLabel.classList.remove('active');
            } else {
                langToggle.classList.remove('en-active');
                if(esLabel) esLabel.classList.add('active');
                if(enLabel) enLabel.classList.remove('active');
            }
        }

        // Store preference
        localStorage.setItem('preferredLang', lang);
    };

    const toggleBtn = document.querySelector('.lang-switcher');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const currentLang = localStorage.getItem('preferredLang') || 'es';
            const newLang = currentLang === 'es' ? 'en' : 'es';
            setLanguage(newLang);
        });
    }

    // Check for stored preference or default to ES
    const savedLang = localStorage.getItem('preferredLang') || 'es';
    setLanguage(savedLang);
});

// Mobile Carousel Engine
let currentExpSlide = 0;
window.moveCarousel = function(direction) {
    if (window.innerWidth > 850 && window.innerHeight > 500) return; // Ensure logic affects mobile OR landscape mobile
    
    const scroller = document.querySelector('.experience-scroller');
    const cards = document.querySelectorAll('.experience-card');
    const total = cards.length;
    
    currentExpSlide += direction;
    
    // Looping constraints
    if (currentExpSlide < 0) currentExpSlide = total - 1;
    if (currentExpSlide >= total) currentExpSlide = 0;
    
    const cardWidth = scroller.clientWidth; // Exactly 85vw
    scroller.scrollTo({
        left: currentExpSlide * cardWidth,
        behavior: 'smooth'
    });
};

window.addEventListener('resize', () => {
    if (window.innerWidth > 850 && window.innerHeight > 500) {
        let scroller = document.querySelector('.experience-scroller');
        if(scroller) scroller.style.transform = 'none';
        currentExpSlide = 0;
    }
});
