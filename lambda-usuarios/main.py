# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from lambda_function import lambda_handler
import json

app = FastAPI()

@app.post("/test")
async def test_lambda(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "El cuerpo de la solicitud debe ser JSON válido"}
        )

    # Captura todos los headers y los normaliza a formato API Gateway
    headers = {k: v for k, v in request.headers.items()}
 


    # Construye el evento simulado como si viniera de API Gateway
    event = {
        "headers": headers,
        "body": body  # Nota: si usas API Gateway con integración Lambda, puede que venga como string
    }

    context = {}  # Contexto simulado
    result = lambda_handler(event, context)

    return JSONResponse(
        status_code=result.get("statusCode", 200),
        content=json_load_safe(result.get("body"))
    )


def json_load_safe(body_str):
    try:
        return json.loads(body_str)
    except:
        return {"raw": body_str}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
