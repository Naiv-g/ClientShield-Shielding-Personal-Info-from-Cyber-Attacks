// Main JavaScript file for Supermarket Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Toggle password visibility
    var togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var targetId = this.getAttribute('data-target');
            var passwordInput = document.getElementById(targetId);
            var icon = this.querySelector('i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Category filter for inventory
    var categorySelect = document.getElementById('category-filter');
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            var currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('category', this.value);
            window.location.href = currentUrl.toString();
        });
    }

    // Sort filters change handler
    var sortBySelect = document.getElementById('sort-by');
    var sortOrderSelect = document.querySelector('select[name="sort_order"]');
    
    if (sortBySelect && sortOrderSelect) {
        sortBySelect.addEventListener('change', function() {
            if (this.form) {
                this.form.submit();
            }
        });
        
        sortOrderSelect.addEventListener('change', function() {
            if (this.form) {
                this.form.submit();
            }
        });
    }

    // Confirm dialog for dangerous actions
    var confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Search form submission
    var searchForms = document.querySelectorAll('.search-form');
    searchForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var searchInput = this.querySelector('input[name="query"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    });

    // Input validation for price and quantity
    var numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            if (this.hasAttribute('min') && parseFloat(this.value) < parseFloat(this.getAttribute('min'))) {
                this.setCustomValidity('Value must be greater than or equal to ' + this.getAttribute('min'));
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Prevent multiple form submissions
    var forms = document.querySelectorAll('form:not(.search-form)');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitButtons = this.querySelectorAll('button[type="submit"], input[type="submit"]');
            submitButtons.forEach(function(button) {
                button.disabled = true;
                if (button.tagName === 'BUTTON') {
                    var originalText = button.innerHTML;
                    button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                    button.setAttribute('data-original-text', originalText);
                }
            });
        });
    });

    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('fade-in');
    });

    // Date inputs - set max date to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    const today = new Date().toISOString().split('T')[0];
    
    dateInputs.forEach(input => {
        if (!input.hasAttribute('max') && input.id.includes('birth')) {
            input.setAttribute('max', today);
        }
    });

    // Table row highlighting
    const tables = document.querySelectorAll('.table-hover');
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.classList.add('highlight');
            });
            
            row.addEventListener('mouseleave', function() {
                this.classList.remove('highlight');
            });
        });
    });

    // Dropdown menu animations
    const dropdownMenus = document.querySelectorAll('.dropdown-menu');
    dropdownMenus.forEach(menu => {
        menu.parentNode.addEventListener('show.bs.dropdown', function() {
            menu.classList.add('fade-in');
        });
    });

    // Welcome animation on dashboard
    const welcomeCard = document.querySelector('.welcome-card');
    if (welcomeCard) {
        welcomeCard.classList.add('welcome-animation');
    }

    // Auto-focus search inputs
    const searchInputs = document.querySelectorAll('input[placeholder*="Search"]');
    if (window.location.href.includes('inventory') || window.location.href.includes('clients') || window.location.href.includes('employees')) {
        searchInputs.forEach(input => {
            if (input.value === '') {
                setTimeout(() => {
                    input.focus();
                }, 500);
            }
        });
    }

    // Low stock warning highlight
    const lowStockItems = document.querySelectorAll('.very-low-stock-warning');
    lowStockItems.forEach(item => {
        const row = item.closest('tr');
        if (row) {
            row.style.backgroundColor = 'rgba(220, 53, 69, 0.1)';
        }
    });

    // Handle CSRF token for AJAX requests
    function getCsrfToken() {
        const csrfElement = document.querySelector('input[name="csrf_token"]');
        return csrfElement ? csrfElement.value : '';
    }

    // Add CSRF token to all AJAX requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Only for same-origin requests
        if (url.startsWith('/') || url.startsWith(window.location.origin)) {
            options.headers = options.headers || {};
            options.headers['X-CSRFToken'] = getCsrfToken();
        }
        return originalFetch(url, options);
    };

    // Form validation helper function
    window.validateFormField = function(input, validationFn, errorMessage) {
        const isValid = validationFn(input.value);
        if (!isValid) {
            input.classList.add('is-invalid');
            let errorDiv = input.nextElementSibling;
            if (!errorDiv || !errorDiv.classList.contains('invalid-feedback')) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                input.parentNode.insertBefore(errorDiv, input.nextElementSibling);
            }
            errorDiv.textContent = errorMessage;
        } else {
            input.classList.remove('is-invalid');
            const errorDiv = input.nextElementSibling;
            if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                errorDiv.textContent = '';
            }
        }
        return isValid;
    };

    // Copy to clipboard function
    window.copyToClipboard = function(text, messageElement) {
        navigator.clipboard.writeText(text)
            .then(function() {
                if (messageElement) {
                    messageElement.textContent = 'Copied!';
                    setTimeout(function() {
                        messageElement.textContent = '';
                    }, 2000);
                }
            })
            .catch(function(err) {
                console.error('Failed to copy: ', err);
                if (messageElement) {
                    messageElement.textContent = 'Failed to copy';
                    setTimeout(function() {
                        messageElement.textContent = '';
                    }, 2000);
                }
            });
    };

    // Function for creating animated counters
    function animateValue(element, start, end, duration) {
        if (!element) return;
        
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const value = Math.floor(progress * (end - start) + start);
            element.textContent = value;
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                element.textContent = end;
            }
        };
        window.requestAnimationFrame(step);
    }

    // Animate stat card numbers
    const statNumbers = document.querySelectorAll('.stats-card .h3');
    statNumbers.forEach(number => {
        const value = parseInt(number.textContent);
        if (!isNaN(value)) {
            number.textContent = '0';
            animateValue(number, 0, value, 1000);
        }
    });

    // Active navigation highlighting
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
            }
        });
    }
    
    setActiveNavItem();

    // Loading state management
    function showLoadingState() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(loadingOverlay);
        return loadingOverlay;
    }

    function hideLoadingState(overlay) {
        if (overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
        }
    }

    // Add loading states to forms with file uploads or long processing
    const longFormSelectors = ['form[enctype="multipart/form-data"]', '.long-processing-form'];
    longFormSelectors.forEach(selector => {
        const forms = document.querySelectorAll(selector);
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                const loadingOverlay = showLoadingState();
                setTimeout(() => hideLoadingState(loadingOverlay), 10000); // Fallback timeout
            });
        });
    });

    // Enhanced error handling for forms
    function handleFormError(form, error) {
        const errorContainer = form.querySelector('.form-errors') || form.querySelector('.alert-danger');
        if (errorContainer) {
            errorContainer.textContent = 'An error occurred: ' + error.message;
            errorContainer.style.display = 'block';
        } else {
            // Create error container if it doesn't exist
            const newErrorContainer = document.createElement('div');
            newErrorContainer.className = 'alert alert-danger';
            newErrorContainer.textContent = 'An error occurred: ' + error.message;
            form.insertBefore(newErrorContainer, form.firstChild);
        }
    }

    // Auto-save functionality for long forms
    function initAutoSave() {
        const autoSaveForms = document.querySelectorAll('[data-autosave="true"]');
        autoSaveForms.forEach(form => {
            const formId = form.id || 'autosave-form';
            let timeout;

            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('input', function() {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        saveFormData(formId, form);
                    }, 2000); // Save after 2 seconds of inactivity
                });
            });

            // Load saved data on page load
            loadFormData(formId, form);
        });
    }

    function saveFormData(formId, form) {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        localStorage.setItem('autosave-' + formId, JSON.stringify(data));
    }

    function loadFormData(formId, form) {
        const savedData = localStorage.getItem('autosave-' + formId);
        if (savedData) {
            const data = JSON.parse(savedData);
            Object.keys(data).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type !== 'hidden' && input.name !== 'csrf_token') {
                    input.value = data[key];
                }
            });
        }
    }

    // Clear autosave data on successful form submission
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.hasAttribute('data-autosave')) {
            const formId = form.id || 'autosave-form';
            localStorage.removeItem('autosave-' + formId);
        }
    });

    // Initialize auto-save functionality
    initAutoSave();
});
