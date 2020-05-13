import os

basedir = os.path.abspath(os.path.dirname(__file__))
skey = 'Jkiy061QVDfLcCu9VS0sYRjGWljaBSG-MFNAktGSwy2J9ThNUOcm9BtmVDrOXk92n4LS59WZuUSHQAlT6e3R_w'

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or skey
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # email config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['superuser-or-admin-email@example.com']