document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const filesList = document.getElementById('filesList');
    const processingModal = new bootstrap.Modal(document.getElementById('processingModal'));

    function loadFiles() {
        fetch('/api/files')
            .then(response => response.json())
            .then(files => {
                filesList.innerHTML = files.map(file => `
                    <tr>
                        <td>${file.filename}</td>
                        <td>${file.filetype}</td>
                        <td>${formatFileSize(file.size)}</td>
                        <td>${new Date(file.created_at).toLocaleString()}</td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="processFile(${file.id})">
                                <i data-feather="play"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteFile(${file.id})">
                                <i data-feather="trash-2"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
                feather.replace();
            });
    }

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Create progress bar
        const progressBar = createProgressBar(file.name);
        
        try {
            const response = await fetch('/api/files', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Upload failed');
            
            showToast('File uploaded successfully', 'success');
            loadFiles();
        } catch (error) {
            showToast(error.message, 'danger');
        } finally {
            progressBar.remove();
        }
    }

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const fileInput = document.getElementById('fileInput');
        
        if (!fileInput.files.length) {
            showToast('Please select a file to upload', 'warning');
            return;
        }
        
        handleFiles(fileInput.files);
        
function createProgressBar(filename) {
    const progressWrapper = document.createElement('div');
    progressWrapper.className = 'progress-wrapper';
    progressWrapper.innerHTML = `
        <div class="d-flex justify-content-between">
            <small>${filename}</small>
            <small class="progress-percentage">0%</small>
        </div>
        <div class="progress">
            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
        </div>
    `;
    document.getElementById('uploadProgress').appendChild(progressWrapper);
    return progressWrapper;
}

function updateProgress(progressWrapper, percentage) {
    const progressBar = progressWrapper.querySelector('.progress-bar');
    const progressText = progressWrapper.querySelector('.progress-percentage');
    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${percentage}%`;
}
        // Show loading state
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Uploading...';
        
        try {
            const response = await fetch('/api/files', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            showToast('File uploaded successfully', 'success');
            loadFiles();
            fileInput.value = '';
        } catch (error) {
            showToast(error.message, 'danger');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        }
    });

    window.processFile = function(fileId) {
        fetch(`/api/process/${fileId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('transcript').textContent = data.transcript;
            document.getElementById('sentiment').textContent = JSON.stringify(data.sentiment, null, 2);
            document.getElementById('entities').textContent = JSON.stringify(data.entities, null, 2);
            document.getElementById('speakers').textContent = JSON.stringify(data.speakers, null, 2);
            processingModal.show();
        });
    };

    window.deleteFile = function(fileId) {
        if (confirm('Are you sure you want to delete this file?')) {
            fetch(`/api/files/${fileId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(() => loadFiles());
        }
    };

    function formatFileSize(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) return '0 Byte';
        const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
    }

    loadFiles();
});
