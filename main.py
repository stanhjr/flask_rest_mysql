from flask_restx import Api
from app import app
from view.account import api as ns_account, account
from view.product import api as ns_product, product

app.register_blueprint(product, url_prefix='/product')
app.register_blueprint(account, url_prefix='/account')

api = Api(version='1.0', title='Test Task API',
          description='entity API',
          authorizations=app.config['AUTHORISATIONS'],
          doc='/doc'
          )

api.add_namespace(ns_product, path='/product')
api.add_namespace(ns_account, path='/account')
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
