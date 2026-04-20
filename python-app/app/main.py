# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.ai import router as ai_router
from app.api.sessions import router as sessions_router
from app.api.stats import router as stats_router
from app.api.system import router as system_router
from app.api.tasks import router as tasks_router
from app.api.uploads import router as uploads_router
from app.config import APP_NAME, APP_VERSION
from app.services.storage import uploads_root


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(tasks_router)
app.include_router(sessions_router)
app.include_router(stats_router)
app.include_router(ai_router)
app.include_router(uploads_router)
app.mount("/uploads", StaticFiles(directory=uploads_root()), name="uploads")
