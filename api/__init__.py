from .recent_open import recent_open_bp
from .reports import reports_bp
from .users import users_bp
from .files import files_bp
from .folders import folders_bp
from .auth import auth_bp
from flask import Blueprint

# Initialize the API blueprint
api_bp = Blueprint('api', __name__)

# Import all the routes for the submodules

# Register the blueprints for each module under the main API blueprint
api_bp.register_blueprint(folders_bp, url_prefix='/folders')
api_bp.register_blueprint(files_bp, url_prefix='/files')
api_bp.register_blueprint(users_bp, url_prefix='/users')
api_bp.register_blueprint(reports_bp, url_prefix='/reports')
api_bp.register_blueprint(recent_open_bp, url_prefix='/recent_open')
api_bp.register_blueprint(auth_bp, url_prefix='/auth')