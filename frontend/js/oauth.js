(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');

    if (token) {
        localStorage.setItem('token', token);
        
        // Clean URL query parameters
        urlParams.delete('token');
        const newQuery = urlParams.toString();
        const cleanUrl = window.location.pathname + (newQuery ? '?' + newQuery : '') + window.location.hash;
        window.history.replaceState({}, document.title, cleanUrl);

        if (window.showToast) {
            window.showToast("Logged in successfully via OAuth!", "success");
        }
        
        if (typeof authService !== 'undefined' && typeof authService.restoreSession === 'function') {
            authService.restoreSession();
        }
    } else if (error) {
        // Clean URL query parameters
        urlParams.delete('error');
        const newQuery = urlParams.toString();
        const cleanUrl = window.location.pathname + (newQuery ? '?' + newQuery : '') + window.location.hash;
        window.history.replaceState({}, document.title, cleanUrl);

        let displayError = decodeURIComponent(error);
        if (displayError.includes(': ')) {
            displayError = displayError.split(': ')[1];
        }

        if (window.showToast) {
            window.showToast(displayError, "error");
        } else {
            console.error("OAuth Error:", displayError);
        }
    }
})();
