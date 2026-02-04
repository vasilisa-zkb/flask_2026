// Quantity counter functionality
document.addEventListener('DOMContentLoaded', function() {
    const decreaseBtn = document.getElementById('decrease-btn');
    const increaseBtn = document.getElementById('increase-btn');
    const quantityDisplay = document.getElementById('quantity-display');
    const quantityInput = document.getElementById('quantity-input');
    
    let quantity = 1;
    
    if (quantityInput) {
        quantityInput.value = quantity;
    }
    
    // Increase quantity
    increaseBtn.addEventListener('click', function() {
        quantity++;
        quantityDisplay.textContent = quantity;
        if (quantityInput) {
            quantityInput.value = quantity;
        }
    });
    
    // Decrease quantity (minimum 1)
    decreaseBtn.addEventListener('click', function() {
        if (quantity > 1) {
            quantity--;
            quantityDisplay.textContent = quantity;
            if (quantityInput) {
                quantityInput.value = quantity;
            }
        }
    });

    // Size selection functionality
    const sizeButtons = document.querySelectorAll('.buttons .button');
    const sizeInput = document.getElementById('size-input');
    const addToCartForm = document.getElementById('add-to-cart-form');
    let selectedSize = null;
    
    sizeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Remove selected class from all buttons
            sizeButtons.forEach(btn => btn.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            selectedSize = this.textContent.trim();
            if (sizeInput) {
                sizeInput.value = selectedSize;
            }
        });
    });

    // Form submission validation
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            if (!selectedSize) {
                e.preventDefault();
                alert('Bitte wählen Sie eine Grösse aus, bevor Sie das Poster in den Warenkorb legen.');
                return false;
            }
        });
    }

    // Carousel functionality
    const carousel = document.querySelector('.carousel');
    if (carousel) {
        const slides = carousel.querySelectorAll('.carousel-slide');
        const prevBtn = carousel.querySelector('.prev');
        const nextBtn = carousel.querySelector('.next');
        const indicators = carousel.querySelectorAll('.indicator');
        let currentIndex = 0;

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
            indicators.forEach((indicator, i) => {
                indicator.classList.toggle('active', i === index);
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

        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', function() {
                currentIndex = index;
                showSlide(currentIndex);
            });
        });

        // Show first slide initially
        showSlide(currentIndex);
    }
});
