// Main JavaScript file for YIASCM Pantry

document.addEventListener('DOMContentLoaded', function () {
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
        themeToggle.addEventListener('click', function () {
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
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation improvements
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Quantity input validation (ensure non-negative numbers)
    const quantityInputs = document.querySelectorAll('input[type="number"]');
    quantityInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            if (this.value < 0) {
                this.value = 0;
            }
        });
    });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function (link) {
        link.addEventListener('click', function (e) {
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

    // Button loading states are now handled in the form submit event above

    // Table row click handlers for better UX
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(function (row) {
        row.addEventListener('mouseenter', function () {
            this.style.backgroundColor = 'rgba(var(--bs-primary-rgb), 0.1)';
        });

        row.addEventListener('mouseleave', function () {
            this.style.backgroundColor = '';
        });
    });

    // Confirmation dialogs for destructive actions
    const deleteButtons = document.querySelectorAll('button[onclick*="confirm"]');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            const message = this.getAttribute('onclick').match(/confirm\('(.+?)'\)/);
            if (message && !confirm(message[1])) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Real-time search functionality (if needed)
    const searchInputs = document.querySelectorAll('input[data-search-target]');
    searchInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            const target = document.querySelector(this.getAttribute('data-search-target'));
            const searchTerm = this.value.toLowerCase();

            if (target) {
                const rows = target.querySelectorAll('tbody tr');
                rows.forEach(function (row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });

    // Auto-refresh for admin dashboard (every 30 seconds)
    if (window.location.pathname.includes('/admin/dashboard')) {
        setInterval(function () {
            // Only refresh if no modals are open and user is active
            if (!document.querySelector('.modal.show') && !document.hidden) {
                window.location.reload();
            }
        }, 30000);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function (e) {
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
            alerts.forEach(function (closeBtn) {
                closeBtn.click();
            });
        }
    });

    // Add visual feedback for form field validation
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(function (control) {
        control.addEventListener('blur', function () {
            if (this.value && this.checkValidity()) {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
            } else if (this.value) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
            }
        });
    });

    // Prevent double submissions with mobile-friendly logic
    forms.forEach(function (form) {
        let submitted = false;
        let submitButton = form.querySelector('button[type="submit"]');
        const isRoundForm = form.id === 'round1Form' || form.id === 'round2Form';

        // For round forms, use simpler mobile-friendly submission
        if (isRoundForm) {
            // Skip complex event handling for mobile if using onclick handlers
            const submitButton = form.querySelector('button[type="submit"]:not([type="button"])');
            
            // Only add complex handling if there's no onclick handler (fallback)
            if (!submitButton || !submitButton.onclick) {
                form.addEventListener('submit', function (e) {
                    if (submitted) {
                        e.preventDefault();
                        return false;
                    }

                    // Check if mobile device
                    const isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent);
                    
                    if (isMobile) {
                        // For mobile, use simple validation and submit
                        e.preventDefault();
                        
                        // Add a delay to ensure all mobile input events have processed
                        setTimeout(() => {
                            const quantityInputs = form.querySelectorAll('.quantity-input');
                            let hasSelection = false;
                            let totalQuantity = 0;

                            console.log('Mobile validation check - total inputs found:', quantityInputs.length);

                            quantityInputs.forEach((input, index) => {
                                // Force refresh the value from the DOM
                                const currentValue = input.value;
                                const numericValue = parseInt(currentValue) || 0;
                                
                                console.log(`Input ${index}: ${input.name} = "${currentValue}" (parsed: ${numericValue})`);
                                
                                if (numericValue > 0) {
                                    hasSelection = true;
                                    totalQuantity += numericValue;
                                }
                                
                                // Ensure value attribute is set for mobile
                                input.setAttribute('value', currentValue);
                            });

                            console.log('Mobile validation result:', { hasSelection, totalQuantity });

                            if (!hasSelection) {
                                alert('Please select at least one item. Current total quantity: ' + totalQuantity);
                                return false;
                            }

                            submitted = true;
                            if (submitButton) {
                                submitButton.disabled = true;
                                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';
                            }

                            // Simple form submission for mobile
                            console.log('Submitting form for mobile device');
                            form.submit();
                        }, 300); // Increased delay to ensure mobile inputs are processed
                        
                    } else {
                        // Desktop logic with more sophisticated handling
                        e.preventDefault();

                        setTimeout(() => {
                            const quantityInputs = form.querySelectorAll('.quantity-input');
                            let hasSelection = false;

                            quantityInputs.forEach(input => {
                                const value = input.value.trim();
                                if (value !== '' && !isNaN(value) && parseInt(value, 10) > 0) {
                                    hasSelection = true;
                                }
                            });

                            if (!hasSelection) {
                                alert('Please select at least one item.');
                                return false;
                            }

                            submitted = true;
                            if (submitButton) {
                                submitButton.disabled = true;
                                const originalText = submitButton.innerHTML;
                                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

                                setTimeout(() => {
                                    submitted = false;
                                    submitButton.disabled = false;
                                    submitButton.innerHTML = originalText;
                                }, 15000);
                            }

                            // Try fetch for desktop, fallback to form.submit()
                            const formData = new FormData(form);
                            
                            if (window.fetch) {
                                fetch(form.action || window.location.pathname, {
                                    method: 'POST',
                                    body: formData,
                                    credentials: 'same-origin'
                                }).then(response => {
                                    if (response.redirected) {
                                        window.location.href = response.url;
                                    } else if (response.ok) {
                                        return response.text().then(html => {
                                            document.open();
                                            document.write(html);
                                            document.close();
                                        });
                                    } else {
                                        throw new Error('Network response was not ok');
                                    }
                                }).catch(error => {
                                    console.error('Fetch submission error:', error);
                                    form.submit();
                                });
                            } else {
                                form.submit();
                            }
                        }, 200);
                    }
                });
            }
        } else {
            // Non-round forms use standard validation
            form.addEventListener('submit', function (event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        }
    });
});

// Mobile quantity control functions
window.increaseQuantity = function (productId) {
    const input = document.getElementById('quantity_' + productId);
    if (input) {
        const currentValue = parseInt(input.value) || 0;
        const newValue = currentValue + 1;
        
        // Update the input value
        input.value = newValue;
        input.setAttribute('value', newValue);
        
        console.log(`Increased quantity for product ${productId}: ${currentValue} -> ${newValue}`);
        
        // Ensure the input is properly focused and updated
        input.focus();
        
        // Trigger multiple events to ensure all handlers are called
        const events = ['input', 'change', 'keyup', 'blur'];
        events.forEach(eventType => {
            const event = new Event(eventType, { 
                bubbles: true, 
                cancelable: true 
            });
            input.dispatchEvent(event);
        });

        // Force update of totals if function exists
        setTimeout(() => {
            if (window.updateTotals && typeof window.updateTotals === 'function') {
                window.updateTotals();
            }
        }, 100);
    }
};

window.decreaseQuantity = function (productId) {
    const input = document.getElementById('quantity_' + productId);
    if (input) {
        const currentValue = parseInt(input.value) || 0;
        if (currentValue > 0) {
            const newValue = currentValue - 1;
            
            // Update the input value
            input.value = newValue;
            input.setAttribute('value', newValue);
            
            console.log(`Decreased quantity for product ${productId}: ${currentValue} -> ${newValue}`);
            
            // Ensure the input is properly focused and updated
            input.focus();
            
            // Trigger multiple events to ensure all handlers are called
            const events = ['input', 'change', 'keyup', 'blur'];
            events.forEach(eventType => {
                const event = new Event(eventType, { 
                    bubbles: true, 
                    cancelable: true 
                });
                input.dispatchEvent(event);
            });

            // Force update of totals if function exists
            setTimeout(() => {
                if (window.updateTotals && typeof window.updateTotals === 'function') {
                    window.updateTotals();
                }
            }, 100);
        }
    }
};

// Utility functions
window.showToast = function (message, type = 'info') {
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

window.formatCurrency = function (amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
};

window.formatDate = function (dateString) {
    return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Debug function for mobile form issues
window.debugMobileForm = function() {
    const form = document.getElementById('round1Form') || document.getElementById('round2Form');
    if (!form) {
        console.log('No round form found');
        return;
    }
    
    console.log('=== Mobile Form Debug ===');
    console.log('User Agent:', navigator.userAgent);
    console.log('Form ID:', form.id);
    
    const allQuantityInputs = form.querySelectorAll('.quantity-input');
    const enabledQuantityInputs = form.querySelectorAll('.quantity-input:not([disabled])');
    console.log('Total quantity inputs found:', allQuantityInputs.length);
    console.log('Enabled quantity inputs found:', enabledQuantityInputs.length);
    
    let hasAnyValue = false;
    enabledQuantityInputs.forEach((input, index) => {
        const value = input.value;
        const name = input.name;
        const parsed = parseInt(value) || 0;
        const classes = input.className;
        
        if (parsed > 0) hasAnyValue = true;
        
        console.log(`Enabled Input ${index}: name="${name}", value="${value}", parsed=${parsed}, classes="${classes}"`);
    });
    
    console.log('Has any values > 0 in enabled inputs:', hasAnyValue);
    
    // Test FormData from enabled inputs only
    const formData = new FormData(form);
    console.log('FormData entries:');
    let formDataHasValues = false;
    for (let [key, value] of formData.entries()) {
        if (key.startsWith('quantity_')) {
            console.log(`  ${key}: ${value}`);
            if (parseInt(value) > 0) formDataHasValues = true;
        }
    }
    
    console.log('FormData has values > 0:', formDataHasValues);
    console.log('=== End Debug ===');
};


