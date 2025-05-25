/**
 * Security Utilities for Supermarket Management System
 * Handles security alerts, input validation, and protection mechanisms
 */

// Function to display security alerts
function showSecurityAlert(message) {
    const securityToast = document.getElementById('securityToast');
    const securityToastMessage = document.getElementById('securityToastMessage');
    
    if (securityToast && securityToastMessage) {
        securityToastMessage.innerHTML = message;
        const bsToast = new bootstrap.Toast(securityToast);
        bsToast.show();
        
        // Add shake animation to toast
        securityToast.classList.add('security-alert');
        setTimeout(() => {
            securityToast.classList.remove('security-alert');
        }, 1000);
        
        // Log the security event (in a real application, this would send to the server)
        console.warn('Security event detected:', message);
    } else {
        // Fallback if toast elements don't exist
        console.warn('Security Alert:', message);
        alert('Security Alert: ' + message);
    }
}

// Set up security monitoring on all pages
document.addEventListener('DOMContentLoaded', function() {
    // Monitor for XSS attempts in form inputs
    function checkForXssAttempts() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const value = this.value.toLowerCase();
                // Check for common XSS patterns
                if (value.includes('<script') || 
                    value.includes('javascript:') || 
                    value.includes('onerror=') || 
                    value.includes('onload=') ||
                    value.includes('onclick=')) {
                    // Clear the suspicious input
                    this.value = this.value.replace(/<script/gi, '')
                                          .replace(/javascript:/gi, '')
                                          .replace(/on\w+=/gi, '');
                    
                    // Show security alert
                    showSecurityAlert('Potential XSS attack detected and blocked.');
                }
            });
        });
    }
    
    // Monitor for SQL injection attempts in form inputs
    function checkForSqlInjectionAttempts() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const value = this.value.toLowerCase();
                // Check for common SQL injection patterns
                if (value.includes('--') || 
                    value.includes(';') || 
                    value.includes('drop table') || 
                    value.includes('1=1') ||
                    value.includes('union select') ||
                    (value.includes("'") && (value.includes('or') || value.includes('and')))) {
                    
                    // Don't clear the input, just warn (for the security demo to work)
                    if (!window.location.pathname.includes('/security_demo')) {
                        this.value = this.value.replace(/--/g, '')
                                            .replace(/;/g, '')
                                            .replace(/drop table/gi, '')
                                            .replace(/1=1/g, '')
                                            .replace(/union select/gi, '');
                        
                        showSecurityAlert('Potential SQL injection attempt detected and blocked.');
                    }
                }
            });
        });
    }
    
    // Validate forms before submission to prevent injection attacks
    function setupFormSecurityValidation() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const inputs = this.querySelectorAll('input[type="text"], input[type="search"], textarea');
                let containsSuspiciousContent = false;
                
                inputs.forEach(input => {
                    const value = input.value.toLowerCase();
                    // Skip validation for security demo page
                    if (window.location.pathname.includes('/security_demo')) {
                        return;
                    }
                    
                    // Check for potentially malicious patterns
                    if (value.includes('<script') || 
                        value.includes('javascript:') || 
                        value.includes('--') || 
                        value.includes(';') || 
                        value.includes('drop table') ||
                        value.includes('1=1') ||
                        value.includes('union select')) {
                        containsSuspiciousContent = true;
                        input.classList.add('is-invalid');
                    }
                });
                
                if (containsSuspiciousContent) {
                    e.preventDefault();
                    showSecurityAlert('Form submission blocked due to suspicious content.');
                }
            });
        });
    }
    
    // Monitor input fields for excessive length that could indicate buffer overflow attempts
    function checkInputLengths() {
        const inputs = document.querySelectorAll('input[type="text"], input[type="search"], textarea');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                // Skip if the input has a max length attribute
                if (this.hasAttribute('maxlength')) {
                    return;
                }
                
                // Check for exceptionally long inputs (potential buffer overflow attempt)
                if (this.value.length > 1000) {
                    this.value = this.value.substring(0, 1000);
                    showSecurityAlert('Input truncated for security reasons. Maximum length: 1000 characters.');
                }
            });
        });
    }
    
    // Add CSRF protection to all AJAX requests
    function setupCsrfProtection() {
        // Get CSRF token from meta tag or form input
        function getCsrfToken() {
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                return metaTag.getAttribute('content');
            }
            
            const csrfInput = document.querySelector('input[name="csrf_token"]');
            if (csrfInput) {
                return csrfInput.value;
            }
            
            return null;
        }
        
        // Add CSRF token to all AJAX requests using the Fetch API
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            const csrfToken = getCsrfToken();
            
            if (csrfToken && (url.startsWith('/') || url.startsWith(window.location.origin))) {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = csrfToken;
            }
            
            return originalFetch(url, options);
        };
        
        // Add CSRF token to all AJAX requests using XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url) {
            const csrfToken = getCsrfToken();
            
            this.addEventListener('readystatechange', function() {
                if (this.readyState === 1 && csrfToken && (url.startsWith('/') || url.startsWith(window.location.origin))) {
                    this.setRequestHeader('X-CSRFToken', csrfToken);
                }
            });
            
            originalXHROpen.apply(this, arguments);
        };
    }
    
    // Monitor for iframe hijacking attempts
    function preventFrameHijacking() {
        if (window.self !== window.top) {
            // The page is in an iframe
            window.top.location = window.self.location;
            showSecurityAlert('Attempted frame hijacking detected and blocked.');
        }
    }
    
    // Detect browser vulnerabilities and show warnings
    function checkBrowserSecurity() {
        // Warning about using older browsers
        const isIE = !!document.documentMode;
        const isOldEdge = !isIE && !!window.StyleMedia;
        
        if (isIE || isOldEdge) {
            showSecurityAlert('You are using an outdated browser with known security vulnerabilities. Please update to a modern browser for better security.');
        }
    }
    
    // Check for suspicious URL parameters
    function checkUrlParameters() {
        const urlParams = new URLSearchParams(window.location.search);
        const suspiciousPatterns = [
            /<script/i,
            /javascript:/i,
            /vbscript:/i,
            /onload=/i,
            /onerror=/i,
            /onclick=/i
        ];
        
        for (let [key, value] of urlParams) {
            for (let pattern of suspiciousPatterns) {
                if (pattern.test(value)) {
                    showSecurityAlert('Suspicious URL parameter detected. Request blocked.');
                    // Redirect to clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    break;
                }
            }
        }
    }
    
    // Setup all security measures
    checkForXssAttempts();
    checkForSqlInjectionAttempts();
    setupFormSecurityValidation();
    checkInputLengths();
    setupCsrfProtection();
    preventFrameHijacking();
    checkBrowserSecurity();
    checkUrlParameters();
    
    // Add custom event listeners for security events
    document.addEventListener('securityevent', function(e) {
        if (e.detail && e.detail.message) {
            showSecurityAlert(e.detail.message);
        }
    });
    
    // Login page specific security
    if (window.location.pathname.includes('/login')) {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            // Monitor for brute force attempts
            let attemptCount = 0;
            
            loginForm.addEventListener('submit', function(e) {
                attemptCount++;
                
                // Show warning after multiple attempts in the same session
                if (attemptCount >= 3) {
                    showSecurityAlert('Multiple login attempts detected. Please ensure you are using the correct credentials.');
                }
                
                // Basic client-side validation to prevent the most obvious attacks
                const usernameInput = document.getElementById('username');
                const passwordInput = document.getElementById('password');
                
                if (usernameInput && (usernameInput.value.includes('<') || usernameInput.value.includes('>'))) {
                    e.preventDefault();
                    usernameInput.value = '';
                    showSecurityAlert('Invalid characters detected in username field.');
                }
                
                if (passwordInput && passwordInput.value.length < 1) {
                    e.preventDefault();
                    showSecurityAlert('Password field cannot be empty.');
                }
            });
        }
    }
    
    // Monitor clipboard operations for sensitive data
    function monitorClipboard() {
        document.addEventListener('copy', function(e) {
            const selection = window.getSelection().toString();
            if (selection.length > 100) {
                showSecurityAlert('Large amount of data copied to clipboard. Please ensure it does not contain sensitive information.');
            }
        });
    }
    
    // Check for developer tools
    function detectDevTools() {
        let devtools = {
            open: false,
            orientation: null
        };
        
        setInterval(() => {
            if (window.outerHeight - window.innerHeight > 160 || window.outerWidth - window.innerWidth > 160) {
                if (!devtools.open) {
                    devtools.open = true;
                    console.warn('Developer tools detected. Please be cautious with sensitive operations.');
                }
            } else {
                devtools.open = false;
            }
        }, 500);
    }
    
    // Monitor for tab/window focus changes during sensitive operations
    function monitorFocusChanges() {
        let sensitiveFormActive = false;
        
        document.addEventListener('focusin', function(e) {
            if (e.target.closest('form')) {
                const form = e.target.closest('form');
                if (form.classList.contains('sensitive-form') || 
                    form.action.includes('login') || 
                    form.action.includes('password')) {
                    sensitiveFormActive = true;
                }
            }
        });
        
        document.addEventListener('focusout', function(e) {
            sensitiveFormActive = false;
        });
        
        window.addEventListener('blur', function() {
            if (sensitiveFormActive) {
                console.warn('Window lost focus during sensitive operation.');
            }
        });
    }
    
    // Initialize additional security monitoring
    monitorClipboard();
    detectDevTools();
    monitorFocusChanges();
});

// Export security functions for use in other scripts
window.showSecurityAlert = showSecurityAlert;

// Function to sanitize strings to prevent XSS
window.sanitizeHtml = function(html) {
    const temp = document.createElement('div');
    temp.textContent = html;
    return temp.innerHTML;
};

// Function to validate email format
window.validateEmail = function(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
};

// Function to validate strong passwords
window.validatePassword = function(password) {
    // At least 8 chars, one number, one uppercase, one lowercase, one special char
    const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return re.test(password);
};

// Security checks for URLs to prevent open redirect vulnerabilities
window.isSafeUrl = function(url) {
    try {
        const parsed = new URL(url, window.location.origin);
        return parsed.origin === window.location.origin;
    } catch (e) {
        // If URL parsing fails, check if it's a relative URL
        return url.startsWith('/') && !url.startsWith('//');
    }
};

// Check if an action should be confirmed by the user
window.confirmSecurityAction = function(message) {
    return confirm(message || 'Are you sure you want to perform this security-sensitive action?');
};

// Log security-related information to the console for debugging
window.logSecurityInfo = function(message, data) {
    console.info('[Security]', message, data || '');
};

// Advanced security utilities
window.SecurityUtils = {
    // Generate secure random tokens
    generateSecureToken: function(length = 32) {
        const array = new Uint8Array(length);
        window.crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    },
    
    // Hash data for integrity checking
    hashData: async function(data) {
        const encoder = new TextEncoder();
        const dataBuffer = encoder.encode(data);
        const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        return hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');
    },
    
    // Validate content security
    validateContent: function(content) {
        const forbiddenPatterns = [
            /<script[\s\S]*?>[\s\S]*?<\/script>/gi,
            /<iframe[\s\S]*?>[\s\S]*?<\/iframe>/gi,
            /javascript:/gi,
            /vbscript:/gi,
            /data:text\/html/gi,
            /on\w+\s*=/gi
        ];
        
        return !forbiddenPatterns.some(pattern => pattern.test(content));
    },
    
    // Rate limiting helper
    createRateLimiter: function(maxRequests, windowMs) {
        const requests = [];
        
        return function() {
            const now = Date.now();
            const windowStart = now - windowMs;
            
            // Remove old requests
            while (requests.length > 0 && requests[0] < windowStart) {
                requests.shift();
            }
            
            if (requests.length >= maxRequests) {
                return false; // Rate limit exceeded
            }
            
            requests.push(now);
            return true; // Request allowed
        };
    }
};
