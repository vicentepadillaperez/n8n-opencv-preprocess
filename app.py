import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import base64

app = FastAPI()


def to_png_b64(img):
    # Codifica la imagen en PNG y luego en base64 (texto)
    success, buf = cv2.imencode(".png", img)
    if not success:
        raise RuntimeError("No se pudo codificar PNG")
    return base64.b64encode(buf).decode("utf-8")


@app.post("/preprocess")
async def preprocess(file: UploadFile = File(...)):
    # 1) Leer imagen
    img_bytes = await file.read()
    npimg = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        return JSONResponse(
            status_code=400,
            content={"error": "No se pudo decodificar la imagen"},
        )

    # 2) Deskew básico (alinear)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = np.column_stack(np.where(gray < 200))
    if coords.size > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
    else:
        angle = 0.0

    (h, w) = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    deskewed = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC)

    # 3) DPI virtual (aumentar tamaño)
    resized = cv2.resize(
        deskewed, None, fx=1.7, fy=1.7, interpolation=cv2.INTER_CUBIC
    )

    # 4) Escala de grises + binarización adaptativa
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35,
        11,
    )

    # 5) Denoise ligero
    clean = cv2.medianBlur(thresh, 3)

    # 6) Segmentación simple en 3 ROIs por altura
    H = clean.shape[0]

    roi_header = clean[0 : int(H * 0.20), :]
    roi_table = clean[int(H * 0.20) : int(H * 0.80), :]
    roi_totals = clean[int(H * 0.80) : H, :]

    return JSONResponse(
        {
            "roi_ids": [to_png_b64(roi_header)],
            "roi_tabla": [to_png_b64(roi_table)],
            "roi_totales": [to_png_b64(roi_totals)],
        }
    )
