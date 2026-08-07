# File Manager - Flask Web App

A professional and minimalist file management website built using **Flask**, **Tailwind CSS**, and **FontAwesome**.

## Features
- No file size limit (no `MAX_CONTENT_LENGTH`)
- Drag & drop and click-to-browse upload
- Real-time upload progress bar (0% - 100%) using XMLHttpRequest
- Loading card with a spinning spinner while uploading
- Floating toast notification (green = Success, red = Error) that automatically disappears after 4 seconds
- Preview, Download, and Delete (with browser confirmation prompt) of files
- Different icons depending on the file type (image, video, PDF, document, archive, audio)
- Secure filename handling using `secure_filename`
- **Optional per-file password protection** (set a password on any file; a password is then required to download it)
- Inline file preview modal (images and text files)

## Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Load the main page |
| POST | `/upload` | Upload a file |
| GET | `/files` | List all files (JSON) |
| GET | `/files/<filename>` | Preview/Download a file |
| GET | `/content/<filename>` | Get text content of a file for inline preview |
| GET | `/download/<filename>` | Force download a file |
| DELETE | `/files/<filename>` | Delete a file |
| GET | `/file-protection/<filename>` | Check if a file has a password set |
| POST | `/set-password/<filename>` | Set or clear a file's password |
| POST | `/secure-download/<filename>` | Verify password and download a protected file |

### Password Protection
- Click the **lock icon** on any file card to set a password for that file.
- Leave the password field empty and click **Save** to remove an existing password.
- When downloading, files **with** a password will prompt for it first.
- Files **without** a password download directly (no prompt).
- Passwords are stored as **SHA-256 hashes** in `passwords.json`.

## How to Run

1. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

3. **Open in the browser:**
   ```
   http://localhost:5000
   ```

Uploaded files are stored in the `uploads/` folder.
