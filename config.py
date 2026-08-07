import os

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
