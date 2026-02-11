document.addEventListener('DOMContentLoaded', () => {
    const quantityControls = document.querySelectorAll('.cart-item-quantity');

    quantityControls.forEach((control) => {
        const cartItem = control.closest('.cart-item');
        const priceEl = cartItem ? cartItem.querySelector('.cart-item-price') : null;
        const valueEl = control.querySelector('.quantity-value');
        const initialQty = parseInt(valueEl.textContent, 10) || 1;
        // data-unit-price contains the per-item unit price (not total), so use it directly
        const storedPrice = priceEl ? parseFloat(priceEl.dataset.unitPrice) : null;
        const unitPrice = (storedPrice !== null && !Number.isNaN(storedPrice)) ? storedPrice : null;
        const buttons = control.querySelectorAll('.quantity-btn');

        if (!valueEl || buttons.length === 0) return;

        const updatePrice = (qty) => {
            if (!priceEl || unitPrice === null || Number.isNaN(unitPrice)) return;
            const total = unitPrice * qty;
            // Always show two decimal places so values like 39.95 are visible
            const formatted = total.toFixed(2);
            priceEl.textContent = `${formatted} CHF`;
        };

        buttons.forEach((btn) => {
            btn.addEventListener('click', async () => {
                const current = parseInt(valueEl.textContent, 10) || 0;
                const isDecrease = btn.getAttribute('aria-label')?.toLowerCase().includes('decrease');
                const next = isDecrease ? Math.max(1, current - 1) : current + 1;
                valueEl.textContent = String(next);
                updatePrice(next);


                const index = cartItem.dataset.index;
                if (index !== undefined) {
                    try {
                        const response = await fetch(`/cart/update/${index}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ quantity: next })
                        });

                        if (!response.ok) {
                            console.error('Failed to update quantity');
                        }
                    } catch (error) {
                        console.error('Error updating quantity:', error);
                    }
                }
            });
        });

        updatePrice(initialQty);
    });

    // Remove button functionality
    const removeButtons = document.querySelectorAll('.remove-button');
    removeButtons.forEach((button) => {
        button.addEventListener('click', async () => {
            const cartItem = button.closest('.cart-item');
            if (!cartItem) return;

            const index = cartItem.dataset.index;
            if (index === undefined) return;

            try {
                const response = await fetch(`/cart/remove/${index}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    window.location.reload();
                } else {
                    console.error('Failed to remove item');
                }
            } catch (error) {
                console.error('Error removing item:', error);
            }
        });
    });
});
