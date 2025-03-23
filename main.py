from fastapi import FastAPI
from api_desubicados import api_desubicados


app = FastAPI()

# Incluir las rutas de las dos APIs
app.include_router(api_desubicados, prefix="/apiDesubicados", tags=["DesUbicados"])
