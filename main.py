import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# origins = ["*"]

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost:3000",
    "http://192.168.200.204:3000",
    "http://192.168.1.2:3000",
    "http://localhost:8080",
    "https://1420-2402-800-6205-305c-d18d-e7a-3231-20dd.ngrok-free.app",
]

app.get("/")(lambda: {"message": "Hello World"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Check if the project has been initialized before
if settings.ENV in ["development"]:
    init_db()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# delete all folders __pycache__ in the project
# `FOR /R . %G IN (__pycache__) DO (IF EXIST "%G" (RMDIR /S /Q "%G"))`

# uninstall all packages in environment python
# `for /F %i in ('pip freeze') do pip uninstall -y %i`

# install all packages in requirements.txt
# `pip install -r requirements.txt`

# remove all unused imports and variables in the project
# `autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .`
