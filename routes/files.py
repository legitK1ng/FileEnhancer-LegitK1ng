from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import File, FileMetadata, db
from datetime import datetime
import os

files_bp = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'wav', 'mp3', 'amr'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@files_bp.route('/')
@login_required
def index():
    return render_template('file_manager.html')

@files_bp.route('/api/files', methods=['GET'])
@login_required
def list_files():
    files = File.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': f.id,
        'filename': f.filename,
        'filetype': f.filetype,
        'size': f.size,
        'created_at': f.created_at.isoformat()
    } for f in files])

@files_bp.route('/api/files', methods=['POST'])
@login_required
def upload_file():
    try:
        # Ensure upload directory exists
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file was uploaded'}), 400
            
        file = request.files['file']
        if not file or file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400
            
        if not allowed_file(str(file.filename)):
            return jsonify({'error': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
            
        # Generate unique filename to prevent overwrites
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Check file size (limit to 50MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size > 50 * 1024 * 1024:  # 50MB in bytes
            return jsonify({'error': 'File size exceeds 50MB limit'}), 400
        file.seek(0)
        
        # Save file
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
            
        # Create database entry
        new_file = File()
        new_file.filename = filename
        new_file.filepath = filepath
        new_file.filetype = str(file.filename).rsplit('.', 1)[1].lower()
        new_file.size = os.path.getsize(filepath)
        new_file.user_id = current_user.id
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'id': new_file.id,
            'filename': new_file.filename,
            'size': formatFileSize(new_file.size),
            'type': new_file.filetype,
            'created_at': new_file.created_at.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

def formatFileSize(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

@files_bp.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        os.remove(file.filepath)
        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
