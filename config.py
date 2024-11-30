# config.py
class Config:
    # Database credentials
    DB_USER = 'u704613426_elsharawyahmed'
    DB_PASSWORD = 'Ahmed**159'
    DB_HOST = 'srv1472.hstgr.io'
    DB_NAME = 'u704613426_reports'

    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
