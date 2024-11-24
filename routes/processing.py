from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import File, FileMetadata, db
from utils.audio_processor import transcribe_audio, diarize_speakers
from utils.text_processor import analyze_sentiment, extract_entities
from datetime import datetime
import queue
import threading
import time

processing_bp = Blueprint('processing', __name__)

# Create a processing queue for each user
processing_queues = {}
processing_status = {}

def get_user_queue():
    user_id = current_user.id
    if user_id not in processing_queues:
        processing_queues[user_id] = queue.Queue()
        processing_status[user_id] = {}
    return processing_queues[user_id], processing_status[user_id]

def process_file_task(file, status_dict):
    try:
        status_dict[file.id] = {
            'status': 'processing',
            'progress': 0,
            'started_at': datetime.utcnow().isoformat()
        }

        if file.filetype in ['wav', 'mp3', 'amr']:
            status_dict[file.id]['progress'] = 25
            transcript = transcribe_audio(file.filepath)
            status_dict[file.id]['progress'] = 50
            speakers = diarize_speakers(file.filepath)
        else:
            with open(file.filepath, 'r') as f:
                transcript = f.read()
            speakers = None
            status_dict[file.id]['progress'] = 50

        status_dict[file.id]['progress'] = 75
        sentiment = analyze_sentiment(transcript)
        entities = extract_entities(transcript)
        
        metadata = FileMetadata(
            file_id=file.id,
            transcript=transcript,
            sentiment_score=sentiment['compound'],
            entities=entities,
            speakers=speakers
        )
        db.session.add(metadata)
        db.session.commit()

        status_dict[file.id] = {
            'status': 'completed',
            'progress': 100,
            'completed_at': datetime.utcnow().isoformat(),
            'results': {
                'transcript': transcript,
                'sentiment': sentiment,
                'entities': entities,
                'speakers': speakers
            }
        }
    except Exception as e:
        status_dict[file.id] = {
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }

def process_queue(user_queue, status_dict):
    while True:
        try:
            file = user_queue.get(timeout=1)
            process_file_task(file, status_dict)
            user_queue.task_done()
        except queue.Empty:
            time.sleep(1)
        except Exception as e:
            print(f"Error in queue processing: {e}")
            time.sleep(1)

@processing_bp.route('/api/process/batch', methods=['POST'])
@login_required
def process_batch():
    file_ids = request.json.get('file_ids', [])
    if not file_ids:
        return jsonify({'error': 'No files specified'}), 400

    user_queue, status_dict = get_user_queue()
    
    # Start processing thread if not already running
    if not any(t.name == f'processor_{current_user.id}' for t in threading.enumerate()):
        processor_thread = threading.Thread(
            target=process_queue,
            args=(user_queue, status_dict),
            name=f'processor_{current_user.id}',
            daemon=True
        )
        processor_thread.start()

    # Queue files for processing
    queued_files = []
    for file_id in file_ids:
        file = File.query.get(file_id)
        if file and file.user_id == current_user.id:
            user_queue.put(file)
            status_dict[file.id] = {
                'status': 'queued',
                'queued_at': datetime.utcnow().isoformat()
            }
            queued_files.append(file_id)

    return jsonify({
        'message': f'Queued {len(queued_files)} files for processing',
        'queued_files': queued_files
    })

@processing_bp.route('/api/process/status', methods=['GET'])
@login_required
def get_processing_status():
    _, status_dict = get_user_queue()
    return jsonify(status_dict)
