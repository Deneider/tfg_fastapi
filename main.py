from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.api_desubicados import api_desubicados


app = FastAPI()

# ruta Api
app.include_router(api_desubicados, prefix="/apiDesubicados", tags=["DesUbicados"])

# ruta web
app.mount("/web", StaticFiles(directory="web", html=True), name="web")
