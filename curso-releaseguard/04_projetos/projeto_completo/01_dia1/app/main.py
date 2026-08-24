from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.routes import router
from app.state.store import state

app=FastAPI(title='ReleaseGuard Store',version='0.1.0')
app.include_router(router)
templates=Jinja2Templates(directory=str(Path(__file__).parent/'web/templates'))

@app.get('/store', response_class=HTMLResponse)
def store_page(request:Request):
    return templates.TemplateResponse(request=request,name='store.html',context={'products':list(state.products.values()),'scenario':state.scenario})

@app.get('/store/checkout', response_class=HTMLResponse)
def checkout_page(request:Request):
    return templates.TemplateResponse(request=request,name='checkout.html',context={'scenario':state.scenario})
