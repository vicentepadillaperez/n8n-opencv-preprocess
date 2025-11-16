from fastapi import FastAPI, File, UploadFile
import cv2
import numpy as np
import base64

app = FastAPI()

def encode_image(img):
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")

@app.post("/preprocess")
async def preprocess(file: UploadFile = File(...)):

    # Leer el archivo subido
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return {"error": "No se pudo leer la imagen"}

    # --- PREPROCESADO BÁSICO ---
    # Escala para DPI virtual
    img_resized = cv2.resize(img, None, fx=1.7, fy=1.7, interpolation=cv2.INTER_CUBIC)

    # Convertir a gris
    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

    # Binarizado OTSU
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Aquí simulo ROIs porque aún no definimos segmentación real
    # (Tú luego definirás las 3 regiones basadas en tu lógica)
    h, w = thresh.shape

    roi_1 = thresh[0:h//3, :]
    roi_2 = thresh[h//3:2*h//3, :]
    roi_3 = thresh[2*h//3:h, :]

    return {
        "roi_ids": [encode_image(roi_1)],
        "roi_tabla": [encode_image(roi_2)],
        "roi_totales": [encode_image(roi_3)]
    }

@app.get("/")
def root():
    return {"status": "ok", "message": "preprocess service running"}
