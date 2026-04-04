from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory=["templates", "templates/partials"])

likes = 0

def inc_like():
    global likes
    likes += 1
    return str(likes)

def reset_like():
    global likes
    likes = 0

@app.get("/home",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"pagina": "/home  /pagina1"})

@app.get("/home/pagina1", response_class=HTMLResponse)
async def pag1(request: Request):
    if not "HX-Request" in request.headers:
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina1"})
    return templates.TemplateResponse(request, "pagina1.html")

@app.get("/home/pagina2", response_class=HTMLResponse)
async def pag2(request: Request):
    if not "HX-Request" in request.headers:
        return templates.TemplateResponse(request, "index.html", {"pagina": "/home/pagina2"})
    return templates.TemplateResponse(request, "pagina2.html")

@app.post("/curtir", response_class=HTMLResponse)
def curtir(request: Request):
    return inc_like()

@app.delete("/curtir", response_class=HTMLResponse)
def curtir(request: Request):
    reset_like()
    return "0"
