import os
import json
import hashlib
import mimetypes
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    abort,
    send_file
)
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------
# Configuration (previously in config.py, now inline)
# ---------------------------------------------------------------
# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory where uploaded files will be stored
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {
    # Images
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'ico',
    # Videos
    'mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'mpeg', 'mpg',
    # PDFs
    'pdf',
    # Documents
    'txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv', 'odt',
    'rtf', 'md', 'html', 'htm', 'json', 'xml', 'py', 'js', 'css',
    # Archives / others
    'zip', 'rar', '7z', 'tar', 'gz', 'mp3', 'wav', 'ogg', 'flac'
}


class Config:
    """
    Application configuration.
    NOTE: No MAX_CONTENT_LENGTH is set intentionally.
    This means there is NO file size limit for uploads.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    UPLOAD_FOLDER = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config.from_object(Config)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Path to the passwords file
PASSWORDS_FILE = os.path.join(app.config['UPLOAD_FOLDER'], '..', 'passwords.json')


def load_passwords():
    """Load the passwords dictionary from disk."""
    if os.path.exists(PASSWORDS_FILE):
        try:
            with open(PASSWORDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_passwords(passwords):
    """Persist the passwords dictionary to disk."""
    with open(PASSWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(passwords, f, indent=2)


def hash_password(password):
    """Return a SHA-256 hash of the given password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def allowed_file(filename):
    """Check if the file extension is allowed."""
    if '.' not in filename:
        return True # extension file dati False
    ext = filename.rsplit('.', 1)[1].lower()
    return True # ext in app.config['ALLOWED_EXTENSIONS']


def human_readable_size(num_bytes):
    """Convert a byte count into a human-friendly string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}" if unit != 'B' else f"{int(num_bytes)} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def get_file_category(filename):
    """Return a category string based on the file extension."""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'webp', 'ico'):
        return 'image'
    if ext in ('mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'mpeg', 'mpg'):
        return 'video'
    if ext == 'pdf':
        return 'pdf'
    if ext in ('txt', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'csv',
               'odt', 'rtf', 'md', 'html', 'htm', 'json', 'xml'):
        return 'document'
    if ext in ('zip', 'rar', '7z', 'tar', 'gz'):
        return 'archive'
    if ext in ('mp3', 'wav', 'ogg', 'flac'):
        return 'audio'
    return 'other'


def list_files_json():
    """Build a list of metadata for all stored files, newest first."""
    upload_dir = app.config['UPLOAD_FOLDER']
    passwords = load_passwords()
    files = []
    try:
        entries = os.listdir(upload_dir)
    except OSError:
        return []

    for fname in entries:
        # Skip hidden/system files (e.g. .gitkeep)
        if fname.startswith('.'):
            continue
        fpath = os.path.join(upload_dir, fname)
        if os.path.isfile(fpath):
            try:
                stat = os.stat(fpath)
            except OSError:
                continue
            mtime = stat.st_mtime
            files.append({
                'name': fname,
                'size': human_readable_size(stat.st_size),
                'size_bytes': stat.st_size,
                'category': get_file_category(fname),
                'modified': datetime.fromtimestamp(mtime).strftime('%B %d, %Y | %H:%M:%S'),
                'mimetype': mimetypes.guess_type(fname)[0] or 'application/octet-stream',
                'protected': fname in passwords,
                '_mtime': mtime
            })
    # Sort: most recently modified first (sort by raw mtime, not the formatted string)
    files.sort(key=lambda x: x['_mtime'], reverse=True)
    # Remove the internal sorting key before returning
    for f in files:
        f.pop('_mtime', None)
    return files


# ---------------------------------------------------------------
# (a) Load the main page
# ---------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------------------------------------------------------
# (b) Upload a file
# ---------------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    # No MAX_CONTENT_LENGTH is set -> no file size limit.
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file was selected.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'}), 400

    if file and allowed_file(file.filename):
        original_name = file.filename
        safe_name = secure_filename(original_name)
        # Ensure name uniqueness
        base, ext = os.path.splitext(safe_name)
        counter = 1
        final_name = safe_name
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], final_name)):
            final_name = f"{base}_{counter}{ext}"
            counter += 1
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], final_name))
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded "{original_name}".',
            'file': final_name
        }), 200

    return jsonify({'success': False, 'message': 'This file type is not supported.'}), 400


# ---------------------------------------------------------------
# (c) List all files (JSON)
# ---------------------------------------------------------------
@app.route('/files')
def files_list():
    files = list_files_json()
    total_size = sum(f['size_bytes'] for f in files)
    return jsonify({
        'success': True,
        'files': files,
        'total_size': human_readable_size(total_size),
        'total_files': len(files)
    })


# ---------------------------------------------------------------
# (d) Download / Preview a file
# ---------------------------------------------------------------
@app.route('/files/<path:filename>')
def download_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(
        directory=app.config['UPLOAD_FOLDER'],
        path=safe_name,
        as_attachment=False
    )


@app.route('/content/<path:filename>')
def file_content(filename):
    """Return the text content of a file for inline preview."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found.'}), 404

    # Only return text content for readable text-based files
    text_exts = {'txt', 'md', 'csv', 'json', 'xml', 'html', 'htm', 'css',
                 'js', 'py', 'log', 'ini', 'yml', 'yaml', 'conf', 'rtf', 'pdf', 'docx'}
    ext = safe_name.rsplit('.', 1)[1].lower() if '.' in safe_name else ''

    if ext not in text_exts:
        return jsonify({'success': False, 'message': 'This file type is not previewable as text.', 'previewable': False}), 415

    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(50000)  # Cap at 50KB to avoid heavy loads
    except Exception:
        return jsonify({'success': False, 'message': 'Could not read the file.'}), 500

    return jsonify({'success': True, 'content': content, 'previewable': True})


@app.route('/download/<path:filename>')
def force_download(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(400)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(
        directory=app.config['UPLOAD_FOLDER'],
        path=safe_name,
        as_attachment=True
    )


# ---------------------------------------------------------------
# (f) File password protection
# ---------------------------------------------------------------
@app.route('/file-protection/<path:filename>')
def file_protection(filename):
    """Check whether a file has a password set."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found.'}), 404

    passwords = load_passwords()
    protected = safe_name in passwords
    return jsonify({'success': True, 'protected': protected})


@app.route('/set-password/<path:filename>', methods=['POST'])
def set_password(filename):
    """Set or clear a password for a file."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found.'}), 404

    data = request.get_json(silent=True) or {}
    password = data.get('password', '')
    current_password = data.get('current_password', '')

    passwords = load_passwords()
    is_protected = safe_name in passwords

    # If the file is already protected, require the current password
    if is_protected:
        provided = hash_password(current_password)
        if provided != passwords[safe_name]:
            return jsonify({'success': False, 'message': 'Incorrect current password.'}), 401

    # If password is empty -> remove protection
    if not password:
        passwords.pop(safe_name, None)
        save_passwords(passwords)
        return jsonify({'success': True, 'message': 'Password removed. The file is now unprotected.', 'protected': False}), 200

    # Otherwise set the password (hashed)
    passwords[safe_name] = hash_password(password)
    save_passwords(passwords)
    return jsonify({'success': True, 'message': 'Password set successfully.', 'protected': True}), 200


@app.route('/secure-download/<path:filename>', methods=['POST'])
def secure_download(filename):
    """Verify the password and return the file as a download."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found.'}), 404

    passwords = load_passwords()

    # If not protected, just download directly
    if safe_name not in passwords:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=safe_name,
            as_attachment=True
        )

    # Otherwise verify the password
    data = request.get_json(silent=True) or {}
    provided = hash_password(data.get('password', ''))
    if provided != passwords[safe_name]:
        return jsonify({'success': False, 'message': 'Incorrect password.'}), 401

    return send_from_directory(
        directory=app.config['UPLOAD_FOLDER'],
        path=safe_name,
        as_attachment=True
    )


@app.route('/verify-password/<path:filename>', methods=['POST'])
def verify_password(filename):
    """Verify the password for a protected file (returns success only)."""
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'success': False, 'message': 'File not found.'}), 404

    passwords = load_passwords()

    # If not protected, allow access
    if safe_name not in passwords:
        return jsonify({'success': True, 'protected': False}), 200

    data = request.get_json(silent=True) or {}
    provided = hash_password(data.get('password', ''))
    if provided != passwords[safe_name]:
        return jsonify({'success': False, 'message': 'Incorrect password.'}), 401

    return jsonify({'success': True, 'protected': True}), 200


# ---------------------------------------------------------------
# (e) Delete a file
# ---------------------------------------------------------------
@app.route('/files/<path:filename>', methods=['DELETE'])
def delete_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({'success': False, 'message': 'Invalid file name.'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        return jsonify({'success': True, 'message': f'Deleted "{safe_name}".'}), 200

    return jsonify({'success': False, 'message': 'File not found.'}), 404


# ---------------------------------------------------------------
# (g) Health check (for Render uptime monitoring / cold start)
# ---------------------------------------------------------------
@app.route('/health')
def health():
    return jsonify({'success': True, 'status': 'ok'}), 200


# ---------------------------------------------------------------
# (h) JSON error handlers (so the frontend always gets JSON)
# ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Resource not found.'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Internal server error. Please try again.'}), 500


if __name__ == '__main__':
    # debug=True only in local development
    debug_mode = os.environ.get('FLASK_DEBUG', '1').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=debug_mode)
