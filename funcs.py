import os, binascii
from config import Config
from werkzeug.utils import secure_filename

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file):
    if file and allowed_file(file.filename):
        random_hex = binascii.b2a_hex(os.urandom(8))
        filename = secure_filename(file.filename)
        _, f_ext = os.path.splitext(filename)
        filename = str(random_hex)+ os.path.splitext(filename)[0] + str(f_ext)
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        return filename
