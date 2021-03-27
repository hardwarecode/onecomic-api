import logging
import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from onecomic.utils import ensure_file_dir_exists
from onecomic.session import CrawlerSession, ImageSession
from onecomic.comicbook import ComicBook
from onecomic.crawlerbase import CrawlerBase
from onecomic.worker import WorkerPoolMgr

from . import config
from .common import get_cookies_path

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    log_level = app.config.get(config.LOG_LEVEL)
    init_logger(level=log_level)
    app.url_map.strict_slashes = False

    if app.config.get('SQLITE_FILE'):
        ensure_file_dir_exists(app.config.get('SQLITE_FILE'))

    db.init_app(app)
    login_manager.init_app(app)

    from .api.views import (
        app as api_app,
        aggregate_app,
        tools_app
    )
    from .manage.views import manage_app
    from .user.views import app as user_app
    from .views import app as index_app
    app.register_blueprint(index_app)
    app.register_blueprint(api_app)
    app.register_blueprint(aggregate_app)
    app.register_blueprint(tools_app)
    app.register_blueprint(manage_app)
    app.register_blueprint(user_app)

    init_crawler(app)
    WorkerPoolMgr.set_worker(config.POOL_SIZE)
    init_db(app)
    if not app.config.get('USERS'):
        app.config['LOGIN_DISABLED'] = True
    return app


def init_crawler(app):
    config = app.config
    CrawlerBase.DRIVER_PATH = config.get('DRIVER_PATH', '')
    CrawlerBase.DRIVER_TYPE = config.get('DRIVER_TYPE', '')
    CrawlerBase.NODE_MODULES = config.get('NODE_MODULES', 'node_modules')
    CrawlerBase.HEADLESS = True
    image_timeout = config.get('IMAGE_TIMEOUT')
    crawler_timeout = config.get('CRAWLER_TIMEOUT')
    proxy_config = app.config.get('CRAWLER_PROXY', {})
    proxy_params = app.config.get('PROXY_PARAMS', {})
    for site in ComicBook.CRAWLER_CLS_MAP:
        proxy = proxy_config.get(site)
        kwargs = proxy_params.get(proxy, {})
        if proxy:
            CrawlerSession.set_proxy(site=site, proxy=proxy, **kwargs)
            ImageSession.set_proxy(site=site, proxy=proxy, **kwargs)
        cookies_path = get_cookies_path(site=site)
        if os.path.exists(cookies_path):
            CrawlerSession.load_cookies(site=site, path=cookies_path)
            ImageSession.load_cookies(site=site, path=cookies_path)
        if image_timeout:
            ImageSession.set_timeout(site=site, timeout=image_timeout)
        if crawler_timeout:
            CrawlerSession.set_timeout(site=site, timeout=crawler_timeout)


def init_db(app):
    if app.config.get('SQLITE_FILE'):
        ensure_file_dir_exists(app.config.get('SQLITE_FILE'))
    with app.app_context():
        db.create_all()


def init_logger(level):
    level = level or logging.INFO
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(lineno)s [%(levelname)s] %(message)s",
        datefmt='%Y/%m/%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
