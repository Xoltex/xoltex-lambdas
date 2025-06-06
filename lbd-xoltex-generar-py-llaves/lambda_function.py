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

COGNITO_ISSUER = "https://us-east-1nff2mkaaw.auth.us-east-1.amazoncognito.com"
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

    if not public_key.verify(message.encode("utf-8"), decoded_sig):
        raise Exception("Firma no válida")

    claims = jwt.decode(
        token,
        public_key.to_pem().decode(),
        algorithms=["RS256"],
        audience=EXPECTED_AUDIENCE,
        issuer=COGNITO_ISSUER
    )
    return claims


def lambda_handler(event, context):
    auth_header = event["headers"].get("authorization", "")
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
    aes_key = get_random_bytes(32)
    aes_b64 = base64.b64encode(aes_key).decode("utf-8")

    # UUID único y tiempo de expiración
    id_acceso = str(uuid.uuid4())
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    response = {
        "idAcceso": id_acceso,
        "rsa": {
            "publicKey": public_key,
            "privateKey": private_key
        },
        "aes": {
            "key": aes_b64,
            "algorithm": "AES-256"
        },
        "expiresAt": expires_at
    }

    return {
        "statusCode": 200,
        "body": json.dumps(response)
    }
