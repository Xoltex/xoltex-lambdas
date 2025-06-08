import json
import uuid
import time
import base64
from datetime import datetime, timedelta, timezone
from jose import jwt
from jose.utils import base64url_decode
from jose import jwk
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import urllib.request
import hashlib
import boto3
from decimal import Decimal


dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CTLlavesAcceso")


COGNITO_ISSUER = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_nFf2mkAAw"
COGNITO_JWKS_URL = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_nFf2mkAAw/.well-known/jwks.json"
EXPECTED_AUDIENCE = "1nm9inu0p0boclg1ocn35ijpnq"


def validate_jwt(token):
    # Obtener llaves públicas de Cognito
    with urllib.request.urlopen(COGNITO_JWKS_URL) as res:
        jwks = json.loads(res.read())

    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if key is None:
        raise Exception("No se encontró la llave pública")
    public_key = jwk.construct(key)
    message, encoded_sig = str(token).rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))
    claims = jwt.decode(
        token,
        public_key.to_pem().decode(), # Volver a la versión original de .to_pem().decode()
        algorithms=["RS256"],
        audience=EXPECTED_AUDIENCE,
        issuer=COGNITO_ISSUER
    )
    return claims


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    llaves_id = path_params.get("llaves")  # Esto extrae el valor del parámetro /llaves/{llaves}

    if llaves_id:
        print("🔎 Buscando llaves con idAcceso:", llaves_id)
        # Aquí haces la búsqueda en DynamoDB
        item = table.get_item(Key={"idAcceso": llaves_id}).get("Item")

        if item:
            return {
                "statusCode": 200,
                "body": json.dumps(item, cls=DecimalEncoder)
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Llave no encontrada"})
            }
        

    auth_header = event["headers"].get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip()

    try:
        claims = validate_jwt(token)
    except Exception as e:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": f"Token inválido: {str(e)}"})
        }

    # Generar RSA
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key().decode("utf-8")
    public_key = rsa_key.publickey().export_key().decode("utf-8")

    # Generar AES (256 bits = 32 bytes)
    aes_key_bytes = get_random_bytes(32)
    aes_b64 = base64.b64encode(aes_key_bytes).decode("utf-8")

    # Generar el hash de la clave AES
    aes_hash = hashlib.sha256(aes_key_bytes).digest()
    aes_hash_b64 = base64.b64encode(aes_hash).decode("utf-8")


    # UUID único y timpo de expiración
    id_acceso = str(uuid.uuid4())
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
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
        "expiresAt": expires_at
    }
   #guaredemos las llaves una una tabla dynamo
    expires_at_unix = int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp())

    table.put_item(Item={
        "idAcceso": id_acceso,
        "rsaPublicKey": public_key,
        "rsaPrivateKey": private_key,
        "aesKey": aes_b64,
        "aesHash": aes_hash_b64,
        "expiresAt": expires_at_unix 
    })

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            # Si quieres todos como float
            return float(o)
        return super(DecimalEncoder, self).default(o)