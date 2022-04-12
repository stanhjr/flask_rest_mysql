from sqlalchemy import func
from passlib.apps import custom_app_context as pwd_context
from app import db, app
from tools.tools import convert_price_output


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128))
    avatar = db.Column(db.String(255), unique=True)
    product = db.relationship('Product')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def set_avatar(self, avatar):
        self.avatar = avatar

    def set_username(self, name):
        self.name = name

    @property
    def get_avatar_link(self):
        return app.config['GENERAL_URL'] + self.avatar


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(255), unique=True, nullable=False)
    vendore_code = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    price = db.relationship('Price')

    def __init__(self, product_name: str, user_id: int):
        self.product_name = product_name
        self.user_id = user_id
        self.vendore_code = self.generate_vendore_code()

    def generate_vendore_code(self):
        max_code = db.session.query(func.max(Product.vendore_code)).filter(Product.user_id == self.user_id).scalar()
        if not max_code:
            max_code = 10001
        else:
            max_code = max_code + 1
        return max_code

    def to_dict(self):
        data = {
            "id": self.id,
            "product_name": self.product_name,
            "image": app.config['GENERAL_URL'] + self.image,
            "vendore_code": self.vendore_code,
            "user_id": self.user_id,
            "price": {model.currency.currency_name: convert_price_output(model.price) for model in self.price}
        }
        return data


class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    currency_name = db.Column(db.String(64), nullable=False)

    def __init__(self, currency_name):
        self.currency_name = currency_name


class Price(db.Model):
    __tablename__ = 'price'
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'))
    currency = db.relationship('Currency', backref="price")

    def __init__(self, price: int):
        self.price = price

