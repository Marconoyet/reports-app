from flask import Flask
from api import api_bp
from db import init_db  # Import the MongoDB initialization function
from config import Config  # Import the configuration
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# Enable CORS for all routes
app = Flask(__name__)
app.config.from_object(Config)  # Load configurations
CORS(app, resources={
     r"/*": {"origins": ["http://localhost:5173", "https://marconoinc.com"]}}, supports_credentials=True, expose_headers=["X-CSRF-TOKEN"])
app.config['JWT_SECRET_KEY'] = 'marconoyet'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = False
# app.config['JWT_COOKIE_CSRF_PROTECT'] = True
# app.config['JWT_CSRF_CHECK_FORM'] = True
# Initialize the MongoDB connection
init_db(app)
JWTManager(app)
# Register the API blueprint

app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)
    #   use_reloader=False
