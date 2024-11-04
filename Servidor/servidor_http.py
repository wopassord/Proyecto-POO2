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
    # Define el directorio base usando `__file__` para apuntar a la raíz del proyecto
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )  # Esto sube un nivel

    # Construye la ruta de `index.html` correctamente desde `base_dir`
    html_path = os.path.join(base_dir, "Servidor", "interfaz_web", "index.html")
    print("Directorio actual:", os.getcwd())
    print("Ruta completa del archivo index.html:", html_path)

    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"Archivo index.html no encontrado en {html_path}"}


# Ruta para mostrar el formulario de inicio de sesión
@app.get("/login")
async def login_form():
    # Usa `base_dir` para la ruta base del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Construye la ruta hacia `login.html`
    html_path = os.path.join(base_dir, "Servidor", "interfaz_web", "login.html")
    print("Ruta completa del archivo login.html:", html_path)

    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"Archivo login.html no encontrado en {html_path}"}


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
    # Usa `base_dir` para la ruta base del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Construye la ruta hacia `dashboard.html`
    dashboard_path = os.path.join(
        base_dir, "Servidor", "interfaz_web", "dashboard.html"
    )
    print("Ruta completa del archivo dashboard.html:", dashboard_path)

    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return {
            "message": f"El archivo dashboard.html no se encuentra en {dashboard_path}"
        }


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
    # Verifica solo una referencia a "Servidor"
    template_path = os.path.abspath(os.path.join("interfaz_web", "ver_imagen.html"))
    print(
        "Ruta de la plantilla HTML:", template_path
    )  # Verifica que el path sea correcto
    try:
        with open(template_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Plantilla HTML no encontrada")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al cargar la plantilla HTML: {str(e)}"
        )


@app.get("/ver-imagen")
async def ver_imagen(image: str = Query(...)):
    # Define el directorio donde están almacenadas las imágenes
    base_dir = os.path.abspath("Servidor/imagenes")
    image_path = os.path.join(base_dir, image)

    # Verificar que el archivo existe antes de procesar la respuesta
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Cargar el contenido de la plantilla HTML
    html_template = load_html_template()
    # Reemplazar la variable en la plantilla por la ruta de la imagen
    html_content = html_template.replace("{{ image_path }}", f"/imagenes/{image}")

    return HTMLResponse(content=html_content)


@app.get("/imagenes/{path}")
async def get_image(path: str):
    base_dir = os.path.abspath("Servidor/imagenes")
    image_path = os.path.join(base_dir, path)

    # Verificar que el archivo existe antes de enviarlo
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Enviar el archivo como respuesta
    return FileResponse(image_path, media_type="image/png")


if __name__ == "__main__":
    print("Iniciando servidor web...")
    uvicorn.run(app, host="127.0.0.1", port=3000)
