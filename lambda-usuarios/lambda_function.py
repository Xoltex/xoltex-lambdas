
import os
import json
from utilidades.logger import log_info
from servicios.ejemplo import ejemplo_servicio

def lambda_handler(event, context):
    log_info("Lambda invocada correctamente.")
    resultado = ejemplo_servicio()
    return {
        "statusCode": 200,
        "body": json.dumps({"mensaje": resultado})
    }
