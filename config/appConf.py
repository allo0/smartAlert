from firebase_admin import credentials
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import os

from starlette.templating import Jinja2Templates

from config.loggingConf import LogConfig
import logging
from logging.config import dictConfig

import firebase_admin

dictConfig(LogConfig().dict())
logger = logging.getLogger("gamewiki")
logging.basicConfig(filename='test.log', filemode='w',
                    encoding='utf-8', format=LogConfig().LOG_FORMAT,
                    )


class Settings:
    PROJECT_NAME: str = "SmartAlerts"
    PROJECT_VERSION: str = "0.5.1"


    # cred = credentials.Certificate("account_key.json")
    # firebase_admin.initialize_app(cred, {
    #     'databaseURL': 'https://smartalert-cdd78-default-rtdb.firebaseio.com/',
    #     'projectId': 'smartalert-cdd78'
    # })

    API_URL = "http://127.0.0.1:8000"
    # API_URL="https://hidden-inlet-35935.herokuapp.com/"

    staticfiles = Jinja2Templates(directory="maps")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    swagger_ui_parameters = {
        "syntaxHighlight.theme": "obsidian"
    }
    swagger_ui_default_parameters = {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    }

    origins = [
        "*",
        "https://hidden-inlet-35935.herokuapp.com/",
        "https://hidden-inlet-35935.herokuapp.com/",
        "http://127.0.0.1:8000",

    ]
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=['*']
        )
    ]
