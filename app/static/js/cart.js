document.addEventListener('DOMContentLoaded', () => {
    const quantityControls = document.querySelectorAll('.cart-item-quantity');

    quantityControls.forEach((control) => {
        const cartItem = control.closest('.cart-item');
        const priceEl = cartItem ? cartItem.querySelector('.cart-item-price') : null;
        const unitPrice = priceEl ? parseFloat(priceEl.dataset.unitPrice) : null;
        const valueEl = control.querySelector('.quantity-value');
        const buttons = control.querySelectorAll('.quantity-btn');

        if (!valueEl || buttons.length === 0) return;

        const updatePrice = (qty) => {
            if (!priceEl || unitPrice === null || Number.isNaN(unitPrice)) return;
            const total = unitPrice * qty;
            const formatted = Number.isInteger(total) ? total : total.toFixed(2);
            priceEl.textContent = `${formatted}.- CHF`;
        };

        buttons.forEach((btn) => {
            btn.addEventListener('click', () => {
                const current = parseInt(valueEl.textContent, 10) || 0;
                const isDecrease = btn.getAttribute('aria-label')?.toLowerCase().includes('decrease');
                const next = isDecrease ? Math.max(1, current - 1) : current + 1;
                valueEl.textContent = String(next);
                updatePrice(next);
            });
        });

        const initialQty = parseInt(valueEl.textContent, 10) || 0;
        updatePrice(initialQty);
    });
});
