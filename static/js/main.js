// Main JavaScript file for YIASCM Pantry

document.addEventListener('DOMContentLoaded', function() {
    // Theme Toggle Functionality
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;
    
    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    function setTheme(theme) {
        if (theme === 'dark') {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            themeIcon.className = 'fas fa-sun';
        } else {
            htmlElement.setAttribute('data-bs-theme', 'light');
            themeIcon.className = 'fas fa-moon';
        }
        localStorage.setItem('theme', theme);
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info):not(.alert-warning)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation improvements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Quantity input validation (ensure non-negative numbers)
    const quantityInputs = document.querySelectorAll('input[type="number"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Add loading states to buttons (but don't interfere with form submission)
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        // Save original button text
        button.setAttribute('data-original-text', button.innerHTML);
        
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                // Only add visual feedback, don't prevent submission
                setTimeout(() => {
                    if (!this.disabled) {
                        this.disabled = true;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                    }
                }, 100);
            }
        });
    });

    // Table row click handlers for better UX
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(var(--bs-primary-rgb), 0.1)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Confirmation dialogs for destructive actions
    const deleteButtons = document.querySelectorAll('button[onclick*="confirm"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('onclick').match(/confirm\('(.+?)'\)/);
            if (message && !confirm(message[1])) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Real-time search functionality (if needed)
    const searchInputs = document.querySelectorAll('input[data-search-target]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const target = document.querySelector(this.getAttribute('data-search-target'));
            const searchTerm = this.value.toLowerCase();
            
            if (target) {
                const rows = target.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });

    // Auto-refresh for admin dashboard (every 30 seconds)
    if (window.location.pathname.includes('/admin/dashboard')) {
        setInterval(function() {
            // Only refresh if no modals are open and user is active
            if (!document.querySelector('.modal.show') && !document.hidden) {
                window.location.reload();
            }
        }, 30000);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                const submitButton = activeForm.querySelector('button[type="submit"]');
                if (submitButton && !submitButton.disabled) {
                    submitButton.click();
                }
            }
        }
        
        // Escape to close alerts
        if (e.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert .btn-close');
            alerts.forEach(function(closeBtn) {
                closeBtn.click();
            });
        }
    });

    // Add visual feedback for form field validation
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(function(control) {
        control.addEventListener('blur', function() {
            if (this.value && this.checkValidity()) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else if (this.value) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    });

    // Enhanced form submission handling for mobile
    forms.forEach(function(form) {
        let submitted = false;
        form.addEventListener('submit', function(e) {
            const isRoundForm = form.id === 'round1Form' || form.id === 'round2Form';
            const isMobile = window.innerWidth <= 768;
            
            // For round forms, do comprehensive validation
            if (isRoundForm) {
                // Force update totals before validation
                if (window.updateTotals && typeof window.updateTotals === 'function') {
                    window.updateTotals();
                }
                
                // Wait a moment for DOM updates on mobile
                if (isMobile) {
                    e.preventDefault();
                    setTimeout(() => {
                        this.validateAndSubmit();
                    }, 200);
                    return false;
                }
                
                // Desktop validation
                if (!this.validateSelection()) {
                    e.preventDefault();
                    return false;
                }
            }
            
            // Prevent double submission
            if (submitted) {
                e.preventDefault();
                return false;
            }
            
            submitted = true;
            
            // Reset after 10 seconds as failsafe
            setTimeout(() => {
                submitted = false;
            }, 10000);
        });
        
        // Add validation method to form
        if (form.id === 'round1Form' || form.id === 'round2Form') {
            form.validateSelection = function() {
                const quantityInputs = this.querySelectorAll('.quantity-input');
                let hasSelection = false;
                let totalSelected = 0;
                
                quantityInputs.forEach(input => {
                    const quantity = parseInt(input.value) || 0;
                    if (quantity > 0) {
                        hasSelection = true;
                        totalSelected += quantity;
                    }
                });
                
                if (!hasSelection || totalSelected === 0) {
                    alert('Please select at least one item before submitting.');
                    return false;
                }
                
                return true;
            };
            
            form.validateAndSubmit = function() {
                if (this.validateSelection()) {
                    // Create a new submit event that bypasses our handler
                    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                    submitEvent.bypassValidation = true;
                    this.dispatchEvent(submitEvent);
                    
                    // If event wasn't cancelled, submit the form
                    if (!submitEvent.defaultPrevented) {
                        this.submit();
                    }
                }
            };
        }
    });
});

// Enhanced mobile quantity control functions
window.increaseQuantity = function(productId) {
    const input = document.getElementById('quantity_' + productId);
    if (input) {
        const currentValue = parseInt(input.value) || 0;
        input.value = currentValue + 1;
        
        // Trigger multiple events to ensure compatibility
        const events = ['input', 'change', 'blur'];
        events.forEach(eventType => {
            const event = new Event(eventType, { bubbles: true, cancelable: true });
            input.dispatchEvent(event);
        });
        
        // Force focus and blur to trigger validation
        input.focus();
        setTimeout(() => {
            input.blur();
            // Force update of totals after a delay
            if (window.updateTotals && typeof window.updateTotals === 'function') {
                window.updateTotals();
            }
        }, 100);
    }
};

window.decreaseQuantity = function(productId) {
    const input = document.getElementById('quantity_' + productId);
    if (input) {
        const currentValue = parseInt(input.value) || 0;
        if (currentValue > 0) {
            input.value = currentValue - 1;
            
            // Trigger multiple events to ensure compatibility
            const events = ['input', 'change', 'blur'];
            events.forEach(eventType => {
                const event = new Event(eventType, { bubbles: true, cancelable: true });
                input.dispatchEvent(event);
            });
            
            // Force focus and blur to trigger validation
            input.focus();
            setTimeout(() => {
                input.blur();
                // Force update of totals after a delay
                if (window.updateTotals && typeof window.updateTotals === 'function') {
                    window.updateTotals();
                }
            }, 100);
        }
    }
};

// Utility functions
window.showToast = function(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
};

window.formatCurrency = function(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
};

window.formatDate = function(dateString) {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

