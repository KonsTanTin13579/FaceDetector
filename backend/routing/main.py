from typing import Optional
from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi import Request

router = APIRouter(prefix="/api", tags=["Мейн 💻"])

templates = Jinja2Templates(directory='C:/Users/vladb/OneDrive/Desktop/tpu_repetitor/tpu_repetitors/frontend/')


@router.get('/start', description="Просмотр результата")
async def start(request: Request):
    return templates.TemplateResponse(name='index.html', context={'request': request})


@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        phone_number: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    return templates.TemplateResponse("register.html",
                                      {"request": request, "phone_number": phone_number, "email": email})

