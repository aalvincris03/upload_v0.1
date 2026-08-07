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

## Deploy to Render.com

### Option A: Deploy via the Render Dashboard (Recommended)
1. Push this repository to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Web Service** → connect your GitHub repo.
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - `SECRET_KEY` — set a long random string (or leave blank to use the dev default)
     - `PYTHON_VERSION` — `3.12.0` (optional if using `runtime.txt`)
4. Click **Create Web Service**. Render will build and deploy automatically.

### Option B: Deploy via `render.yaml` (Blueprint)
1. Push this repository (which includes `render.yaml`) to GitHub.
2. On Render, go to **New** → **Blueprint** → select the repo.
3. Render will read `render.yaml` and create the service automatically.

### ⚠️ Important Notes
- **Ephemeral storage**: Render uses an ephemeral filesystem. Uploaded files and `passwords.json` are **lost on every restart/redeploy**. This is fine for testing, but for permanent storage you would need to integrate an external service (e.g., AWS S3, a database, etc.).
- The `Procfile` is already included so Render knows to run `gunicorn app:app`.
- The `.gitignore` excludes `uploads/`, `passwords.json`, and other local files from being committed to GitHub.
