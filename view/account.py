import os.path

from flask_restx import Resource, Namespace
from flask import Blueprint, request, send_from_directory
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required

from models import User
from app import app, db
from tools.tools import save_image, get_api_json, allowed_file, CustomException
from view.schemas import sign_up_fields, sign_up_response, error_response, login_fields, login_response, \
    refresh_response, upload_account_parser, edit_response

account = Blueprint('account', __name__)
api = Namespace('account', description='User actions with an account')
api.models.update({
    "SignUpFields": sign_up_fields,
    "SignUpResponse": sign_up_response,
    "ErrorResponse": error_response,
    "LoginFields": login_fields,
    "LoginResponse": login_response,
    "RefreshResponse": refresh_response,
    "EditResponse": edit_response,

})


@api.route('/sign_up', methods=['POST'])
class SignUp(Resource):
    @api.expect(sign_up_fields, validate=True)
    @api.response(201, 'CREATED', sign_up_response)
    @api.response(400, 'BAD REQUEST', error_response)
    def post(self):
        """
        User registration, login password
        """
        data = request.get_json(force=True)
        login = data.get("login")
        password = data.get("password")
        if not login or not password:
            return {"msg": "login and password fields must be filled"}, 400
        if User.query.filter_by(login=login).first() is not None:
            return {"msg": "login already exists"}, 400
        user = User(login=login)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return {'login': user.login}, 201


@api.route("/login", methods=["POST"])
class Login(Resource):
    @api.expect(login_fields, validate=True)
    @api.response(202, "ACCEPTED", login_response)
    @api.response(400, 'BAD REQUEST', error_response)
    @api.response(401, 'UNAUTHORIZED', error_response)
    def post(self):
        """
        User login, login password
        :return JWT
        """
        data = request.get_json(force=True)
        login = data.get("login")
        password = data.get("password")
        if not login or not password:
            return {"msg": "login and password fields must be filled"}, 400
        user = User.query.filter(User.login == login).first()
        if not user or not user.verify_password(password):
            return {"msg": "Bad username or password"}, 401

        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {'access_token': access_token, "refresh_token": refresh_token, "user_id": user.id}, 202


@api.route("/refresh", methods=["POST"])
class Refresh(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, "OK", refresh_response)
    @api.response(422, 'UNPROCESSABLE ENTITY', error_response)
    @api.response(401, 'UNAUTHORIZED', error_response)
    @jwt_required(refresh=True)
    def post(self):
        """
        refresh JWT
        """
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {'access_token': access_token}, 200


@api.route("/edit")
class AccountUpdate(Resource):
    @jwt_required()
    @api.expect(upload_account_parser, validate=True)
    @api.response(201, "CREATED", edit_response)
    @api.response(400, 'BAD REQUEST', error_response)
    @api.response(401, 'UNAUTHORIZED', error_response)
    @api.response(422, "UNPROCESSABLE ENTITY", error_response)
    @api.doc(security='Bearer Auth')
    def post(self):
        """
        Edit user profile, image and name
        """
        try:
            data = get_api_json(request)
            args = upload_account_parser.parse_args()
            image = args.get('avatar')
            name = data.get("name")
            if not name and not image:
                return {"msg": "all fields are empty"}, 400

            if not allowed_file(image.filename):
                raise CustomException(message="file type is not supported")

            pk = str(get_jwt_identity())
            user = db.session.query(User).filter(User.id == pk).first()
            response = dict()

            if image:
                image_link = save_image(image, 'avatar', pk)
                user.avatar = image_link
                db.session.add(user)
                response.update(avatar_link=user.get_avatar_link)

            if name:
                user.name = name
                db.session.add(user)
                response.update(name=name)

            db.session.commit()

        except CustomException as e:
            return {"msg": str(e)}, 400

        return response, 201


@account.route('/download', methods=['GET'])
@jwt_required()
def download_image():
    """
    Get image avatar from a link
    """
    try:
        user_id = str(get_jwt_identity())
        name = request.args.get('path')
        path_to_folder = os.path.join(app.config['UPLOAD_FOLDER_AVATAR'], user_id)
        return send_from_directory(path_to_folder, name, as_attachment=True)
    except TypeError:
        return {"msg": "not enough arguments"}, 400
