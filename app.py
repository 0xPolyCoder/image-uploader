import os
import uuid
from flask import *
from werkzeug.utils import secure_filename
from functools import wraps
import filetype
from whitenoise import WhiteNoise
import logging


#--------config--------
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_TYPES = {'png', 'jpg', 'jpeg', 'gif'}


# The presence of the WHITELISTED_IP environment variable enables IP checking
WHITELISTED_IP = os.getenv('WHITELISTED_IP') # If this variable is not set, the IP whitelist is disabled
if WHITELISTED_IP:
    app.logger.info(f"IP Whitelisting is ENABLED for IP: {WHITELISTED_IP}")
else:
    app.logger.info("IP Whitelisting is DISABLED. The app is publicly accessible.")

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '1337-super-secret-key-lol')
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/', prefix='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload size
#--------end config--------


#--------helper funcs--------
def validate_image(file_stream):
    # filetype.guess needs at least the first 261 bytes
    header = file_stream.read(261)
    file_stream.seek(0) # Rewind the stream so Flask can save it later

    kind = filetype.guess(header)
    if kind is None:
        print("filetype: Cannot guess file type.")
        return None

    app.logger.info(f"filetype guessed: MIME='{kind.mime}', Extension='{kind.extension}'")

    if kind.extension.lower() in ALLOWED_IMAGE_TYPES:
        return kind
    
    app.logger.warning(f"Validation failed: Type '{kind.extension}' is not in ALLOWED_IMAGE_TYPES.")
    return None
#--------end help funcs--------


#--------IP Whitelist decorator--------
def ip_whitelist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If the WHITELISTED_IP variable is not set, skip the check entirely
        if not WHITELISTED_IP:
            return f(*args, **kwargs)

        # Determine the client's real IP, checking the proxy header first
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            # The first IP in the X-Forwarded-For list is the original client
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            # If not behind a proxy, use the direct connection IP
            client_ip = request.remote_addr

        # Check if the client's IP matches the whitelisted IP
        if client_ip != WHITELISTED_IP:
            app.logger.warning(f"Forbidden access attempt from IP: {client_ip}")
            abort(403)  # Forbidden

        return f(*args, **kwargs)
    return decorated_function
#--------IP Whitelist decorator--------



#--------routes--------
@app.route('/')
@ip_whitelist_required
def index():
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    try:
        # Sort images by modification time, newest first
        image_files = os.listdir(app.config['UPLOAD_FOLDER'])
        images = sorted(
            image_files,
            key=lambda x: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], x)),
            reverse=True
        )
    except FileNotFoundError:
        images = []
    return render_template('index.html', images=images)


@app.route('/upload', methods=['POST'])
@ip_whitelist_required
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        # If no file is submitted, redirect back to the index page
        return redirect(url_for('index'))
        
    file = request.files['file']

    # Validate the file content, not the filename
    image_type = validate_image(file.stream)

    if file and image_type:
        # generate a secure, random filename. Ignore user input
        filename = f"{uuid.uuid4().hex}.{image_type.extension}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    
    return "Invalid file type", 400


@app.route('/uploads/<filename>')
@ip_whitelist_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete/<filename>')
@ip_whitelist_required
def delete_file(filename):
    # Sanitize filename to prevent any path traversal.
    safe_filename = secure_filename(filename)
    
    # Check that the sanitized name is the same as the original, ensuring nothing like '../' was passed
    if safe_filename != filename:
        abort(400, "Invalid filename.")

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    
    # Ensure the file is actually in the UPLOAD_FOLDER before deleting.
    # os.path.abspath is used for security to resolve the full path.
    if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        abort(403, "Attempt to access file outside of upload directory.")

    if os.path.exists(file_path):
        os.remove(file_path)
        
    return redirect(url_for('index'))
#--------end Routes--------


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)