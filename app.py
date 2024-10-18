from flask import Flask
from api import api_bp
from db import init_db  # Import the MongoDB initialization function
from config import Config  # Import the configuration
from flask import Flask
from flask_cors import CORS

# Enable CORS for all routes
app = Flask(__name__)
app.config.from_object(Config)  # Load configurations
CORS(app)

# Initialize the MongoDB connection
init_db(app)

# Register the API blueprint

app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)
    #   use_reloader=False
