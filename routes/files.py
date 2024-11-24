from flask import Blueprint, request, jsonify, render_template, current_app
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

@files_bp.route('/api/files/upload-chunk', methods=['POST'])
@login_required
def upload_chunk():
    try:
        chunk = request.files.get('chunk')
        chunk_number = int(request.form.get('chunkNumber'))
        total_chunks = int(request.form.get('totalChunks'))
        filename = request.form.get('filename')
        upload_id = request.form.get('uploadId')
        file_size = int(request.form.get('fileSize'))
        
        if not all([chunk, chunk_number is not None, total_chunks, filename, upload_id]):
            return jsonify({'error': 'Missing required chunk upload data'}), 400
            
        # Validate total file size (10GB limit)
        if file_size > 10 * 1024 * 1024 * 1024:
            return jsonify({'error': 'File size exceeds 10GB limit'}), 400
            
        temp_dir = os.path.join(current_app.config['TEMP_FOLDER'], upload_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        chunk_file = os.path.join(temp_dir, f'chunk_{chunk_number}')
        chunk.save(chunk_file)
        
        # Track upload progress
        progress = {
            'uploadId': upload_id,
            'filename': filename,
            'chunkNumber': chunk_number,
            'totalChunks': total_chunks,
            'progress': (chunk_number + 1) / total_chunks * 100
        }
        
        # If this is the last chunk, combine all chunks
        if chunk_number == total_chunks - 1:
            final_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                        f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{secure_filename(filename)}")
            
            with open(final_filepath, 'wb') as final_file:
                for i in range(total_chunks):
                    chunk_path = os.path.join(temp_dir, f'chunk_{i}')
                    with open(chunk_path, 'rb') as chunk_file:
                        final_file.write(chunk_file.read())
            
            # Cleanup temp files
            import shutil
            shutil.rmtree(temp_dir)
            
            # Create database entry
            new_file = File(
                filename=filename,
                filepath=final_filepath,
                filetype=filename.rsplit('.', 1)[1].lower() if '.' in filename else '',
                size=os.path.getsize(final_filepath),
                user_id=current_user.id
            )
            db.session.add(new_file)
            db.session.commit()
            
            return jsonify({
                'status': 'complete',
                'file': {
                    'id': new_file.id,
                    'filename': new_file.filename,
                    'size': formatFileSize(new_file.size),
                    'type': new_file.filetype,
                    'created_at': new_file.created_at.isoformat()
                }
            })
        
        return jsonify({
            'status': 'in_progress',
            'progress': progress
        })
            
        if not file.filename or not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Supported types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
            
        # Generate unique filename to prevent overwrites
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Check file size (limit to 200MB)
        file.seek(0, os.SEEK_END)
        size = file.tell()
        if size > 200 * 1024 * 1024:  # 200MB in bytes
            return jsonify({'error': 'File size exceeds 200MB limit'}), 400
        file.seek(0)
        
        # Validate file content
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if file_ext in ['txt', 'pdf']:
            try:
                content = file.read(1024)  # Read first 1KB to validate
                file.seek(0)
                content.decode('utf-8')  # Try to decode as text
            except UnicodeDecodeError:
                return jsonify({'error': 'Invalid text file encoding'}), 400
        elif file_ext in ['wav', 'mp3', 'amr']:
            try:
                content = file.read(44)  # Read header
                file.seek(0)
                if not any(content.startswith(header) for header in [b'RIFF', b'ID3', b'#!AMR']):
                    return jsonify({'error': 'Invalid audio file format'}), 400
            except Exception:
                return jsonify({'error': 'Invalid audio file'}), 400
        
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
