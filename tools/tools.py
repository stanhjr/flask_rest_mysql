import json
from decimal import Decimal
import os
import glob
from flask import url_for
from werkzeug.utils import secure_filename
from app import app


class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_image(image_file, image_type: str, user_id, vendore_code=None):
    user_id = str(user_id)
    filename = secure_filename(image_file.filename)
    if image_type == 'avatar':
        dir_name = os.path.join(app.config['UPLOAD_FOLDER_AVATAR'], user_id)
        url = 'account.download_image'
    elif image_type == 'product_image':
        vendore_code = str(vendore_code)
        dir_name = os.path.join(app.config['UPLOAD_FOLDER_PRODUCT'], user_id)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        dir_name = os.path.join(dir_name, vendore_code)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        url = 'product.upload_image'

        image_link = url_for(url, pk=user_id, vendore_code=vendore_code, path=filename)
        files = glob.glob(f'{dir_name}/*')
        for f in files:
            os.remove(f)
        image_file.save(os.path.join(dir_name, filename))
        return image_link

    else:
        raise CustomException(message="image type not found")

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # filename = secure_filename(image_file.filename)
    image_link = url_for(url, pk=user_id, vendore_code=vendore_code, path=filename)

    files = glob.glob(f'{dir_name}/*')
    for f in files:
        os.remove(f)
    image_file.save(os.path.join(dir_name, filename))

    return image_link


def get_api_json(req) -> dict:
    """
    :param req: API request
    :return: Request JSON or raise HeadersTypeException
    """
    request_json = req.get_json(silent=True)
    if not request_json:
        try:
            request_json = json.loads(req.headers.get('data'))
        except (TypeError, ValueError, json.decoder.JSONDecodeError) as e:
            raise CustomException(message="headers type is data is not supported, example {'name': 'string'}")

    return request_json


def convert_price_input(price):
    return int(price * 100)


def convert_price_output(price):
    price = Decimal(price / 100)
    return str(price.quantize(Decimal('1.00')))


