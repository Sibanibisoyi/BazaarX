/* BazaarX Custom JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // 1. Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.padding = '0.5rem 0';
                navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            } else {
                navbar.style.padding = '1rem 0';
                navbar.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
            }
        });
    }

    // 2. Product Image Switcher (Detail Page)
    const mainImage = document.getElementById('mainProductImage');
    const thumbnails = document.querySelectorAll('.thumbnail-img');

    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const newSrc = this.getAttribute('src');
                mainImage.setAttribute('src', newSrc);

                // Active state
                thumbnails.forEach(t => t.classList.remove('border-primary', 'border-2'));
                this.classList.add('border-primary', 'border-2');
            });
        });
    }

    // 3. Back to Top Button
    const backToTopBtn = document.getElementById('backToTopBtn');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopBtn.style.display = 'flex';
                backToTopBtn.style.opacity = '1';
            } else {
                backToTopBtn.style.opacity = '0';
                setTimeout(() => {
                    if (window.scrollY <= 300) {
                        backToTopBtn.style.display = 'none';
                    }
                }, 300);
            }
        });

        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 4. Quantity Stepper Enhancements
    const qtyInputs = document.querySelectorAll('input[name="quantity"]');
    qtyInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) this.value = 1;
        });
    });

    // 5. Toast Notifications Autohide
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // ─────────────────────────────────────────────────────────────
    // 6. AJAX Add to Cart — Amazon-style toast
    //    Uses EVENT DELEGATION on document so it catches every form
    //    whether present at load time or added later (infinite scroll)
    // ─────────────────────────────────────────────────────────────
    let cartToastTimer = null;

    function showCartToast(status, message) {
        var toast  = document.getElementById('cartToast');
        var icon   = document.getElementById('cartToastIcon');
        var title  = document.getElementById('cartToastTitle');
        var msgEl  = document.getElementById('cartToastMsg');
        var header = document.getElementById('cartToastHeader');
        if (!toast) return;

        if (status === 'success') {
            icon.className          = 'fas fa-check-circle';
            icon.style.color        = '#00c851';
            title.textContent       = 'Added to Cart';
            header.style.background = '#232f3e';
        } else if (status === 'warning') {
            icon.className          = 'fas fa-exclamation-circle';
            icon.style.color        = '#f0c14b';
            title.textContent       = 'Notice';
            header.style.background = '#7b5e00';
        } else {
            icon.className          = 'fas fa-times-circle';
            icon.style.color        = '#ff4444';
            title.textContent       = 'Error';
            header.style.background = '#c0392b';
        }

        msgEl.textContent = message;

        // Restart slide-in animation
        toast.style.display = 'none';
        void toast.offsetWidth;
        toast.style.display = 'block';

        if (cartToastTimer) clearTimeout(cartToastTimer);
        cartToastTimer = setTimeout(function() {
            toast.style.display = 'none';
        }, 4000);
    }

    function updateCartBadge(count) {
        var badge = document.getElementById('cartItemCount');
        if (!badge) return;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    // Single delegated listener — catches ALL cart forms including
    // those inside dynamically loaded content (infinite scroll etc.)
    document.addEventListener('submit', function(e) {
        var form = e.target;
        if (!form || !form.action) return;

        // Only intercept Add-to-Cart forms
        if (form.action.indexOf('/cart/add/') === -1) return;

        e.preventDefault();
        e.stopPropagation();

        var formData = new FormData(form);
        var btn = form.querySelector('button[type="submit"], input[type="submit"]');
        var origHTML = null;

        // Show spinner on the button
        if (btn) {
            origHTML = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            setTimeout(function() {
                btn.disabled  = false;
                btn.innerHTML = origHTML;
            }, 1800);
        }

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
            body: formData,
        })
        .then(function(res) {
            var ct = res.headers.get('content-type') || '';
            if (!ct.includes('application/json')) {
                // Not JSON — likely a redirect to login page
                throw new Error('not-json');
            }
            return res.json();
        })
        .then(function(data) {
            showCartToast(data.status, data.message);
            if (typeof data.cart_count !== 'undefined') {
                updateCartBadge(data.cart_count);
            }
        })
        .catch(function(err) {
            if (err.message === 'not-json') {
                window.location.href = '/users/login/?next=' + encodeURIComponent(form.action);
            } else {
                showCartToast('error', 'Could not add item. Please try again.');
            }
        });
    });

});
