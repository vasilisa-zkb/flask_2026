
document.addEventListener('DOMContentLoaded', function () {
    const decreaseBtn = document.getElementById('decrease-btn');
    const increaseBtn = document.getElementById('increase-btn');
    const quantityDisplay = document.getElementById('quantity-display');
    const quantityInput = document.getElementById('quantity-input');

    let quantity = 1;

    if (quantityInput) {
        quantityInput.value = quantity;
    }


    increaseBtn.addEventListener('click', function () {
        quantity++;
        quantityDisplay.textContent = quantity;
        if (quantityInput) {
            quantityInput.value = quantity;
        }
    });


    decreaseBtn.addEventListener('click', function () {
        if (quantity > 1) {
            quantity--;
            quantityDisplay.textContent = quantity;
            if (quantityInput) {
                quantityInput.value = quantity;
            }
        }
    });


    const sizeButtons = document.querySelectorAll('.buttons button');
    const sizeInput = document.getElementById('size-input');
    const addToCartForm = document.getElementById('add-to-cart-form');
    const priceDisplay = document.querySelector('.price');
    let selectedSize = null;

    // Use numeric unit prices and format to two decimals when displaying
    const sizePrice = {
        'A4': 38.95,
        'A3': 46.95,
        'A2': 54.95
    };

    sizeButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            sizeButtons.forEach(btn => btn.classList.remove('selected'));

            this.classList.add('selected');
            selectedSize = this.id.toUpperCase();
            if (sizeInput) {
                sizeInput.value = selectedSize;
            }

            if (priceDisplay && sizePrice[selectedSize] !== undefined) {
                priceDisplay.textContent = sizePrice[selectedSize].toFixed(2) + ' CHF';
            }
        });
    });


    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function (e) {
            if (!selectedSize) {
                e.preventDefault();
                alert('Bitte wählen Sie eine Grösse aus, bevor Sie das Poster in den Warenkorb legen.');
                return false;
            }
        });
    }


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

        prevBtn.addEventListener('click', function () {
            currentIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(currentIndex);
        });

        nextBtn.addEventListener('click', function () {
            currentIndex = (currentIndex + 1) % slides.length;
            showSlide(currentIndex);
        });

        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', function () {
                currentIndex = index;
                showSlide(currentIndex);
            });
        });


        showSlide(currentIndex);
    }
});