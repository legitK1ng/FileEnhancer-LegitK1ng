from flask import Blueprint, request, jsonify
from flask_login import login_required
from models import File, FileMetadata, db
from utils.audio_processor import transcribe_audio, diarize_speakers
from utils.text_processor import analyze_sentiment, extract_entities

processing_bp = Blueprint('processing', __name__)

@processing_bp.route('/api/process/<int:file_id>', methods=['POST'])
@login_required
def process_file(file_id):
    file = File.query.get_or_404(file_id)
    
    try:
        if file.filetype in ['wav', 'mp3', 'amr']:
            transcript = transcribe_audio(file.filepath)
            speakers = diarize_speakers(file.filepath)
        else:
            with open(file.filepath, 'r') as f:
                transcript = f.read()
            speakers = None
            
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
        
        return jsonify({
            'transcript': transcript,
            'sentiment': sentiment,
            'entities': entities,
            'speakers': speakers
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
