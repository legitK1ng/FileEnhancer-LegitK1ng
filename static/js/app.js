// Global app initialization and utility functions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize feather icons
    feather.replace();

    // Global error handler for fetch requests
    window.handleFetchError = async (response) => {
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'An error occurred');
        }
        return response;
    };

    // Configure global toast notifications
    window.showToast = (message, type = 'info') => {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }

        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type}`;
        toastEl.setAttribute('role', 'alert');
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.getElementById('toast-container').appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl);
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    };

    // File type validation
    window.validateFileType = (file) => {
        const allowedTypes = ['text/plain', 'audio/wav', 'audio/mp3', 'audio/amr', 'application/pdf'];
        if (!allowedTypes.includes(file.type)) {
            showToast('Invalid file type', 'danger');
            return false;
        }
        return true;
    };

    // File size formatting
    window.formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Date formatting
    window.formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    // Setup global progress indicator
    const progressIndicator = document.createElement('div');
    progressIndicator.className = 'progress-indicator d-none';
    progressIndicator.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(progressIndicator);

    window.showProgress = () => {
        progressIndicator.classList.remove('d-none');
    };

    window.hideProgress = () => {
        progressIndicator.classList.add('d-none');
    };

    // Handle session expiration
    document.addEventListener('fetch', (event) => {
        if (event.response?.status === 401) {
            window.location.href = '/login';
        }
    });

    // Add global keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'u': // Upload file
                    e.preventDefault();
                    document.querySelector('#fileInput')?.click();
                    break;
                case 'f': // Focus search
                    e.preventDefault();
                    document.querySelector('.search-input')?.focus();
                    break;
            }
        }
    });

    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Handle theme toggle if present
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
});

