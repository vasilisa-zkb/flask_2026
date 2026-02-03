// Quantity counter functionality
document.addEventListener('DOMContentLoaded', function() {
    const decreaseBtn = document.getElementById('decrease-btn');
    const increaseBtn = document.getElementById('increase-btn');
    const quantityDisplay = document.getElementById('quantity-display');
    
    let quantity = 1;
    
    // Increase quantity
    increaseBtn.addEventListener('click', function() {
        quantity++;
        quantityDisplay.textContent = quantity;
    });
    
    // Decrease quantity (minimum 1)
    decreaseBtn.addEventListener('click', function() {
        if (quantity > 1) {
            quantity--;
            quantityDisplay.textContent = quantity;
        }
    });

    // Size selection functionality
    const sizeButtons = document.querySelectorAll('.buttons .button');
    let selectedSize = null;
    
    sizeButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all buttons
            sizeButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            selectedSize = this.id;
        });
    });

    // Carousel functionality
    const carousel = document.querySelector('.carousel');
    if (carousel) {
        const slides = carousel.querySelectorAll('.carousel-slide');
        const prevBtn = carousel.querySelector('.prev');
        const nextBtn = carousel.querySelector('.next');
        let currentIndex = 0;

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
        }

        prevBtn.addEventListener('click', function() {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(currentIndex);
        });

        nextBtn.addEventListener('click', function() {
            currentIndex = (currentIndex + 1) % slides.length;
            showSlide(currentIndex);
        });

        // Show first slide initially
        showSlide(currentIndex);
    }
});
