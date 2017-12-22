"""
This is the entry point to the application
"""
from flask import Blueprint, Flask
from flask_assets import Bundle, Environment

# Controllers/blueprints
from app.controllers import (
    account, currency, vanguard, distributions, assetallocation, index,
    portfolio, price, securities, settings, transaction)

# Define the WSGI application object
app = Flask(__name__, static_url_path='/static')
# Configurations
app.config.from_object('config')
# Register blueprints
app.register_blueprint(index.index_controller)
app.register_blueprint(account.account_controller)
app.register_blueprint(assetallocation.assetallocation_controller)
app.register_blueprint(currency.currency_controller)
app.register_blueprint(distributions.distribution_controller)
app.register_blueprint(portfolio.portfolio_controller)
app.register_blueprint(price.price_controller)
app.register_blueprint(settings.settings_controller)
app.register_blueprint(securities.stock_controller)
app.register_blueprint(transaction.transaction_controller)
app.register_blueprint(vanguard.vanguard_controller)

scripts_route = Blueprint('scripts', __name__, static_url_path='/scripts',
                          static_folder='scripts')
app.register_blueprint(scripts_route)
fa_route = Blueprint('fa', __name__, static_url_path='/fonts',
                     static_folder='node_modules/font-awesome/fonts')
app.register_blueprint(fa_route)

# Bundles
bundles = {
    'vendor_css': Bundle(
        #'../node_modules/@fortawesome/fontawesome/styles.css',
        #'../node_modules/@fortawesome/fontawesome-free-solid',
        '../node_modules/font-awesome/css/font-awesome.min.css',
        '../node_modules/daterangepicker/daterangepicker.css',
        '../node_modules/datatables.net-bs4/css/dataTables.bootstrap4.css',
        '../node_modules/select2/dist/css/select2.min.css',
        output='vendor.css'),
    'vendor_js': Bundle(
        '../node_modules/popper.js/dist/umd/popper.min.js',
        '../node_modules/jquery/dist/jquery.min.js',
        '../node_modules/moment/min/moment.min.js',
        '../node_modules/daterangepicker/daterangepicker.js',
        '../node_modules/bootstrap/dist/js/bootstrap.min.js',
        '../node_modules/datatables.net/js/jquery.dataTables.js',
        '../node_modules/datatables.net-bs4/js/dataTables.bootstrap4.js',
        '../node_modules/select2/dist/js/select2.min.js',
        output='vendor.js'),
    # 'site_css': Bundle(
    #     'site.scss',
    #     filters='pyscss',
    #     output='site.css')
    'site_js': Bundle(
        '../scripts/basic.js',
        output='site.js'
    )
}
assets = Environment(app)
assets.register(bundles)


##################################################################################
if __name__ == '__main__':
    # Use debug=True to enable template reloading while the app is running.
    # debug=True <= this is now controlled in config.py.
    app.run()