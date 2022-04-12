import os

from flask import Blueprint, request, jsonify, send_from_directory
from flask_restx import Resource, Namespace
from sqlalchemy import desc
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Product, Price, Currency
from app import db, app
from tools.tools import save_image, allowed_file, CustomException, get_api_json, convert_price_input
from view.schemas import upload_product_parser, add_product_response, error_response, get_product_parser, \
    get_product_response

product = Blueprint('product', __name__)
api = Namespace('product', description='User actions with an product')

api.models.update({
    "AddProductResponse": add_product_response,
    "GetProductResponse": get_product_response
})


@api.route('/add_product', methods=["POST"])
class AddProduct(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')
    @api.expect(upload_product_parser, validate=True)
    @api.response(201, 'CREATED', add_product_response)
    @api.response(400, 'BAD REQUEST', error_response)
    @api.response(401, 'UNAUTHORIZED', error_response)
    @api.response(422, 'UNPROCESSABLE ENTITY', error_response)
    def post(self):
        """
        Adding a product to the user's product list
        """
        try:
            data = get_api_json(request)
            args = upload_product_parser.parse_args()

            image = args.get('image')
            price_dict = data.get("price")
            product_name = data.get("product_name")

            if not product_name and not image and not price_dict:
                return {"msg": "one of the fields is not filled"}, 400

            if not allowed_file(image.filename):
                raise CustomException(message="file type is not supported")

            product = Product(user_id=get_jwt_identity(),
                              product_name=product_name)

            product.image = save_image(image_file=image,
                                       image_type='product_image',
                                       user_id=get_jwt_identity(),
                                       vendore_code=product.vendore_code)

            currency = db.session.query(Currency)

            for currency_name in price_dict:
                currency.filter(Currency.currency_name == currency_name)
            currency_list = currency.all()

            for obj in currency_list:
                if obj.currency_name in price_dict:
                    price_value = price_dict.get(obj.currency_name)
                    price = Price(price=convert_price_input(price_value))
                    obj.price.append(price)
                    product.price.append(price)
                    price_dict.pop(obj.currency_name)

            if price_dict:
                for currency_name, price_value in price_dict.items():
                    price = Price(price=convert_price_input(price_value))
                    currency = Currency(currency_name=currency_name)
                    currency.price.append(price)
                    product.price.append(price)

            db.session.add(product)
            db.session.commit()

        except CustomException as e:
            return {"msg": str(e)}, 400

        return product.to_dict(), 201


@api.route('/get_product', methods=["GET"])
class AddProduct(Resource):
    @jwt_required()
    @api.doc(security='Bearer Auth')
    @api.expect(get_product_parser, validate=True)
    @api.response(200, 'OK', get_product_response)
    @api.response(400, 'BAD REQUEST', error_response)
    @api.response(401, 'UNAUTHORIZED', error_response)
    @api.response(422, 'UNPROCESSABLE ENTITY', error_response)
    def get(self):
        """
        Get a list of products with the options to sort and filter
        """
        try:
            data = request.args
            product_name = data.get('product_name')
            vendore_code = data.get('vendore_code')
            sort = data.get('sort')
            page_number = int(data.get('page_number')) or 1
            page_size = int(data.get('page_size')) or 10
            user_id = get_jwt_identity()

            product_list = db.session.query(Product).filter(Product.user_id == user_id)

            if vendore_code:
                product_list = product_list.filter(Product.vendore_code == vendore_code).first()
                return product_list.to_dict(), 200
            if product_name:
                product_list = product_list.filter(Product.product_name.contains(product_name))

            if sort == 'product_name':
                product_list = product_list.order_by(Product.product_name)

            elif sort == 'vendore_code':
                product_list = product_list.order_by(desc(Product.vendore_code))

            product_list = product_list.paginate(page=page_number, per_page=page_size)
            page = product_list.page
            product_list = product_list.items

            response = {product_list.index(model) + 1: model.to_dict() for model in product_list}
            response.update(page=page)
            return response, 200

        except CustomException as e:
            return {"msg": str(e)}, 400

        except ValueError:
            return {"msg": "input data is not valid"}, 400


@product.route('/download/<pk>', methods=['GET', 'POST'])
@jwt_required()
def upload_image(pk):
    """
    Get image product from a link
    """
    try:
        if int(pk) != get_jwt_identity():
            return jsonify({"msg": " No access to content"}), 403
        name = request.args.get('path')
        user_id = str(get_jwt_identity())
        vendore_code = request.args.get('vendore_code')
        path_to_folder = os.path.join(app.config['UPLOAD_FOLDER_PRODUCT'], user_id)
        path_to_folder = os.path.join(path_to_folder, vendore_code)
        return send_from_directory(path_to_folder, name, as_attachment=True)
    except TypeError:
        return {"msg": "not enough arguments"}, 400
