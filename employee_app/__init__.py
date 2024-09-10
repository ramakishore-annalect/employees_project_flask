import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://avnadmin:{DB_PASSWORD}@pg-2eade052-kishore88-20d6.c.aivencloud.com:14147/defaultdb?sslmode=require"  # Default for development
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()  # Initialize without the app
ma = Marshmallow(app)

def create_app(config_name=None):
    """Factory function to create the Flask app with dynamic configuration."""
    global app  # Access the global app instance

    if config_name:
        app.config.from_object(config_name) 

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register the blueprint only if it hasn't been registered before
    if not hasattr(app, 'extensions'):  # Check if extensions have been initialized
        app.extensions = {}  # Initialize extensions dictionary if it doesn't exist
    if 'blueprints_registered' not in app.extensions:
        from employee_app.blueprint import employee_bp
        app.register_blueprint(employee_bp, url_prefix='/employee')
        app.extensions['blueprints_registered'] = True  # Mark blueprints as registered

    return app

# Create the default app for development
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008) #ssl_context=('cert.pem', 'key.pem'))
