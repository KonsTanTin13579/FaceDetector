from fastapi import FastAPI
from backend.routing.main import router

app = FastAPI()
app.include_router(router)