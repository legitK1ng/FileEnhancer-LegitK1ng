# File Management System

A Flask-based file management system with audio/text processing capabilities.

## Features

- File upload and management
- Audio file transcription
- Speaker diarization
- Text analysis and sentiment detection
- Entity extraction
- Batch processing capabilities

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd file-management-system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the values according to your configuration

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
python main.py
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL database connection URL
- `FLASK_SECRET_KEY`: Secret key for Flask session management
- `UPLOAD_FOLDER`: Directory for file uploads
- `MAX_CONTENT_LENGTH`: Maximum allowed file size (default: 10GB)

## Dependencies

- Flask and Flask extensions
- SQLAlchemy
- SpeechRecognition
- pydub
- scikit-learn
- NLTK
- spaCy
- psycopg2-binary
- python-dotenv

## Usage

1. Register an account or login
2. Upload files through the web interface
3. Process files individually or in batch
4. View processing results and analysis
