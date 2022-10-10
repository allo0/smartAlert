from fastapi import FastAPI, Depends
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config.appConf import Settings
from source.models.firebase.firebase_models import FirebaseConfig
from source.models.google_router import backendGoogleRouter

app = FastAPI(title=Settings.PROJECT_NAME, version=Settings.PROJECT_VERSION,
              middleware=Settings.middleware, swagger_ui_parameters=Settings.swagger_ui_parameters,
              swagger_ui_default_parameters=Settings.swagger_ui_default_parameters)

# app.add_middleware(HTTPSRedirectMiddleware)

# https://linuxtut.com/en/6fc3792d034c2a01b830/
# https://pypi.org/project/fastapi-healthcheck/
# https://firebase.google.com/docs/admin/setup#windows
# https://morioh.com/p/a593f973aff0

app.include_router(backendGoogleRouter, prefix='/v1/googleB')
