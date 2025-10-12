from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_mysqldb import MySQL
from flask_login import LoginManager

mysql = MySQL()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.secret_key = 'Admin123'

    app.config['MYSQL_HOST'] = '' #replace with your mysql host
    app.config['MYSQL_USER'] = '' #replace with your mysql user
    app.config['MYSQL_PASSWORD'] = '' #replace with your mysql password
    app.config['MYSQL_DB'] = 'artspace' #create a database name artspace for consistency
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    # Initialize Flask extensions
    mysql.init_app(app)
    bootstrap = Bootstrap5(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from . import views
    app.register_blueprint(views.main)

    # Error Handlers
    @app.errorhandler(404) 
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500

    # Load session module
    from . import session
    
    return app