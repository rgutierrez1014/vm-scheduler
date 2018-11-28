from webapp2 import WSGIApplication

from config import get_config, get_app_env
from routes import routes


def create_app():
    return WSGIApplication(routes=routes, config=get_config(), debug=(get_app_env() == 'development'))
