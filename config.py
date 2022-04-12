from datetime import timedelta
from jwt_keys.jwt_keys import RSA_PRIVATE, RSA_PUBLIC


class Configuration(object):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:111@localhost/flask_db'
    SQLALCHEMY_ECHO = False
    JWT_ALGORITHM = 'RS256'
    SECRET_KEY = 'mysecret'
    JWT_PRIVATE_KEY = RSA_PRIVATE
    JWT_PUBLIC_KEY = RSA_PUBLIC
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER_PRODUCT = './images/product'
    UPLOAD_FOLDER_AVATAR = './images/avatar'
    GENERAL_URL = 'http://127.0.0.1:5000'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    AUTHORISATIONS = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
    }
