from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import File, FileMetadata, db
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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        
        new_file = File(
            filename=filename,
            filepath=filepath,
            filetype=file.filename.rsplit('.', 1)[1].lower(),
            size=os.path.getsize(filepath),
            user_id=current_user.id
        )
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({
            'id': new_file.id,
            'filename': new_file.filename
        })
        
    return jsonify({'error': 'Invalid file type'}), 400

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
