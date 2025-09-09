from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
from pathlib import Path

ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif','pdf','txt','csv','zip','json','xlsx','mp3','mp4','avi','mkv','mov','txt','doc','docx','ppt','pptx'}
DEFAULT_MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024  # 10 GB per request

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', DEFAULT_MAX_CONTENT_LENGTH))

    # Ensure upload folder exists
    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

    @app.get('/')
    def index():
        return render_template('index.html', allowed=', '.join(sorted(ALLOWED_EXTENSIONS)))

    @app.post('/upload')
    def upload():
        saved = []
        errors = []

        # Single file input named "file"
        if 'file' in request.files:
            f = request.files['file']
            if f and f.filename:
                if allowed_file(f.filename):
                    filename = secure_filename(f.filename)
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    saved.append(filename)
                else:
                    errors.append(f"File type not allowed: {f.filename}")

        # Multiple file input named "files"
        if 'files' in request.files:
            for f in request.files.getlist('files'):
                if f and f.filename:
                    if allowed_file(f.filename):
                        filename = secure_filename(f.filename)
                        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        saved.append(filename)
                    else:
                        errors.append(f"File type not allowed: {f.filename}")

        if not saved and not errors:
            flash('No files selected.', 'warning')

        if saved:
            flash('Uploaded: ' + ', '.join(saved), 'success')
        for e in errors:
            flash(e, 'danger')

        return redirect(url_for('index'))

    @app.get('/files')
    def list_files():
        try:
            names = sorted([n for n in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], n))])
        except FileNotFoundError:
            names = []
        return render_template('files.html', files=names)

    @app.get('/files/<path:filename>')
    def download(filename):
        safe_name = secure_filename(filename)
        if not allowed_file(safe_name):
            abort(403)
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_name, as_attachment=True)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # For local development only
    app.run(host='0.0.0.0', port=port, debug=True)
