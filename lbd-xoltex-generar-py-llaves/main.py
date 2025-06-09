# main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from lambda_function import lambda_handler
import json

app = FastAPI()

@app.get("/llaves")
async def test_lambda(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "El cuerpo de la solicitud debe ser JSON válido"}
        )
    headers = {k.title(): v for k, v in request.headers.items()}
    event = {
        "headers": headers,
        "body": body  
    }
    context = {}  
    result = lambda_handler(event, context)
    return result
    
@app.get("/llaves/{llaves}")
async def test_lambda(request: Request, llaves: str):
    try:
        body = await request.json()
    except Exception:
        body = {}  
    # Captura headers y normalízalos
    headers = {k.title(): v for k, v in request.headers.items()}
    # Evento simulado como si fuera de API Gateway
    event = {
        "headers": headers,
        "pathParameters": {
            "llaves": llaves  
        },
        "body": json.dumps(body)  
    }
    context = {} 
    result = lambda_handler(event, context)

    return result

def json_load_safe(body_str):
    try:
        return json.loads(body_str)
    except:
        return {"raw": body_str}


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
