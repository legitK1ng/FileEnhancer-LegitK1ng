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

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const fileInput = document.getElementById('fileInput');
        const submitButton = this.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        
        if (!fileInput.files.length) {
            showToast('Please select a file to upload', 'warning');
            return;
        }
        
        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
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
