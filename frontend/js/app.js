// Data Research Engineer - Frontend Application
console.log('Data Research Engineer application loaded');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing application...');
    
    // Add any initialization code here
    initializeApp();
});

function initializeApp() {
    console.log('Application initialized successfully');
    
    // Add event listeners for interactive elements
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('click', function() {
            console.log('Feature card clicked:', this.querySelector('h3').textContent);
        });
    });
} 