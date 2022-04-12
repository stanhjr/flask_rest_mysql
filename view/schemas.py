from flask_restx import Model, fields
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage


# ----------------------------ACCOUNT PARSERS----------------------------------

upload_account_parser = RequestParser()
upload_account_parser.add_argument('avatar',
                                   location='files',
                                   type=FileStorage,
                                   required=False,
                                   help='"png", "jpg", "jpeg"')

upload_account_parser.add_argument('data',
                                   location='headers',
                                   type=str,
                                   required=False,
                                   help='{"name": "String"}'
                                   )

# ----------------------------ACCOUNT MODELS----------------------------------

login_fields = Model("LoginFields", {
    "login": fields.String(required=True),
    "password": fields.String(required=True),
})

sign_up_fields = Model("SignUpFields", {
    "login": fields.String(required=True),
    "password": fields.String(required=True),
})

sign_up_response = Model("SignUpResponse", {
    "login": fields.String(description='User login'),
    "password": fields.String(description='User password')
})
login_response = Model('LoginResponse', {
    "access_token": fields.String,
    "refresh_token": fields.String,
    "user_id": fields.Integer,
})

refresh_response = Model('RefreshResponse', {
    "access_token": fields.String,
})

edit_response = Model('EditResponse', {
    "name": fields.String,
    "image_link": fields.String
})

error_response = Model('ErrorResponse', {
    'msg': fields.String,
})

headers = {
    "Content-Type": "application/json",
    "Content-Disposition": "attachment; filename=foobar.json"
}

# ----------------------------PRODUCT PARSERS----------------------------------

upload_product_parser = RequestParser()
upload_product_parser.add_argument('image',
                                   location='files',
                                   type=FileStorage,
                                   required=False,
                                   help='"png", "jpg", "jpeg"')

upload_product_parser.add_argument('data',
                                   location='headers',
                                   type=str,
                                   required=False,
                                   help='{"product_name": "potato", "price": {"euro": 10, "dollar": 20}}')

get_product_parser = RequestParser()
get_product_parser.add_argument('sort', type=str, location='args', required=False, help='product_name or vendore_code')

get_product_parser.add_argument('product_name', type=str, location='args', required=False, help='potato')

get_product_parser.add_argument('vendore_code', type=str, location='args', required=False, help='10002')

get_product_parser.add_argument("page_number", type=int, required=False, default=1, help="page_number")
get_product_parser.add_argument("page_size", type=int, required=False, default=10, help="page_size")

# ----------------------------PRODUCT MODELS----------------------------------

add_product_response = Model('AddProductResponse', {
    "id": fields.Integer,
    "product_name": fields.String,
    "image": fields.String,
    "vendore_code": fields.String,
    "user_id": fields.Integer,
    "price": fields.Raw
})

get_product_response = Model('GetProductResponse', {
    "id": fields.Integer,
    "product_name": fields.String,
    "image": fields.String,
    "vendore_code": fields.String,
    "user_id": fields.Integer,
    "page": fields.Integer(example=1),
    "price": fields.Raw
})
