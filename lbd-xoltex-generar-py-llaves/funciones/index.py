from excepciones.errores import AppError
from utilidades.folio_context import obtener_folio
from servicios.insertarDynamo import insertar
import json
import hashlib
import boto3
import base64
from datetime import datetime, timedelta, timezone
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from decimal import Decimal
from utilidades.validar_jwt import validate_jwt


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CTLlavesAcceso")

class funcion:
    def crearLLaves(path_params,event):
        llaves_id = path_params.get("llaves")

        if llaves_id:
            item = table.get_item(Key={"idAcceso": llaves_id}).get("Item")
            if not item:
                raise AppError(404, "Llave no encontrada")
            return json.loads(json.dumps(item, cls=DecimalEncoder))


        auth_header = event["headers"].get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise AppError(401, "Falta token o formato incorrecto")

        token = auth_header.replace("Bearer ", "").strip()
        validate_jwt(token)

        # Generar llaves RSA y AES
        rsa_key = RSA.generate(2048)
        private_key = rsa_key.export_key().decode("utf-8")
        public_key = rsa_key.publickey().export_key().decode("utf-8")
        aes_key_bytes = get_random_bytes(32)
        aes_b64 = base64.b64encode(aes_key_bytes).decode("utf-8")
        aes_hash = hashlib.sha256(aes_key_bytes).digest()
        aes_hash_b64 = base64.b64encode(aes_hash).decode("utf-8")
        id_acceso = str(obtener_folio())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        expires_at_unix = int(expires_at.timestamp())

        response = {
            "idAcceso": id_acceso,
            "rsa": {
                "publicKey": public_key,
                "privateKey": private_key
            },
            "aes": {
                "accesoSimetrico": aes_b64,
                "codigoHash": aes_hash_b64
            },
            "expiresAt": expires_at_unix
        }
        insertar(response)
        return response


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)
