from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from starlette.responses import FileResponse, RedirectResponse
import os
from interprete_gcode import UtilGcode

app = FastAPI()
gcode_interprete = UtilGcode()


class LoginData(BaseModel):
    username: str
    password: str


@app.get("/")
async def index_page():
    html_path = os.path.join("Servidor", "interfaz_web", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": "Archivo index.html no encontrado"}


# Ruta para mostrar el formulario de inicio de sesión
@app.get("/login")
async def login_form():
    html_path = os.path.join("Servidor", "interfaz_web", "login.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": "Archivo index.html no encontrado"}


# Ruta para procesar el inicio de sesión
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Logica del login
    #
    #
    #
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard")
async def dashboard():
    # Ruta al archivo dashboard.html
    dashboard_path = os.path.join("Servidor", "interfaz_web", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return {"message": "El archivo dashboard.html no se encuentra"}


@app.post("/carga-gcode")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        file_content_str = file_content.decode("latin-1")  # Decodificar a string
        image_path = gcode_interprete.subir_archivo_gcode(
            file.filename, file_content_str, True
        )
        if image_path is None:
            raise ValueError("Error al generar la imagen")

        # Extraer el nombre del archivo de imagen desde el path
        image_name = os.path.basename(image_path)

        # Redireccionar a `/ver-imagen` con el nombre de la imagen
        return RedirectResponse(f"/ver-imagen?image={image_name}", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cargar el archivo HTML como plantilla
def load_html_template():
    template_path = os.path.join("Servidor", "interfaz_web", "ver_imagen.html")
    with open(template_path, "r") as f:
        return f.read()


@app.get("/ver-imagen")
async def ver_imagen(image: str = Query(...)):
    image_path = os.path.join("Servidor", "imagenes", image)
    # Asegurarse de que el archivo existe antes de enviarlo al HTML
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    html_template = load_html_template()
    html_content = html_template.replace("{{ image_path }}", f"/imagenes/{image}")

    return HTMLResponse(content=html_content)


@app.get("/imagenes/{path}")
async def get_image(path: str):
    image_path = os.path.join("Servidor", "imagenes", path)

    # Verificar si el archivo existe en el sistema de archivos
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Devolver la imagen como respuesta de archivo
    return FileResponse(image_path, media_type="image/png")


if __name__ == "__main__":
    print("Iniciando servidor web...")
    uvicorn.run(app, host="127.0.0.1", port=3000)
