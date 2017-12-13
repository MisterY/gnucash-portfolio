"""
This is the entry point to the application
"""
from flask import Flask, render_template, request
from flask_assets import Bundle, Environment
from gnucash_portfolio import get_vanguard_au_prices
from flask import Blueprint

# Controllers/blueprints
from controllers import account, vanguard, income, assetallocation, index, portfolio, securities, settings, transaction

# Define the WSGI application object
app = Flask(__name__, static_url_path='/static')
# Configurations
app.config.from_object('config')
# Register blueprints
app.register_blueprint(index.index_controller)
app.register_blueprint(account.account_controller)
app.register_blueprint(assetallocation.assetallocation_controller)
app.register_blueprint(vanguard.vanguard_controller)
app.register_blueprint(income.income_controller)
app.register_blueprint(portfolio.portfolio_controller)
app.register_blueprint(securities.stock_controller)
app.register_blueprint(settings.settings_controller)
app.register_blueprint(transaction.transaction_controller)

scripts_route = Blueprint('scripts', __name__, static_url_path='/scripts', static_folder='scripts')
app.register_blueprint(scripts_route)
fa_route = Blueprint('fa', __name__, static_url_path='/fonts', static_folder='node_modules/font-awesome/fonts')
app.register_blueprint(fa_route)

# Bundles
bundles = {
    'vendor_css': Bundle(
        #'../node_modules/@fortawesome/fontawesome/styles.css',
        #'../node_modules/@fortawesome/fontawesome-free-solid',
        '../node_modules/font-awesome/css/font-awesome.min.css',
        '../node_modules/daterangepicker/daterangepicker.css',
        output='vendor.css'),
    'vendor_js': Bundle(
        '../node_modules/popper.js/dist/umd/popper.min.js',
        '../node_modules/jquery/dist/jquery.min.js',
        '../node_modules/moment/min/moment.min.js',
        '../node_modules/daterangepicker/daterangepicker.js',
        '../node_modules/bootstrap/dist/js/bootstrap.min.js',
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
