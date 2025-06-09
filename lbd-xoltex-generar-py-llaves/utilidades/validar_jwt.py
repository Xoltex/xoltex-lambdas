from excepciones.errores import AppError
import json
from jose import jwt, jwk
import urllib.request
from jose.utils import base64url_decode

COGNITO_ISSUER = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_nFf2mkAAw"
COGNITO_JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"
EXPECTED_AUDIENCE = "1nm9inu0p0boclg1ocn35ijpnq"

def validate_jwt(token):
    with urllib.request.urlopen(COGNITO_JWKS_URL) as res:
        jwks = json.loads(res.read())
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]
    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if key is None:
        raise AppError(401, "No se encontró la llave pública")
    public_key = jwk.construct(key)
    message, encoded_sig = str(token).rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))
    claims = jwt.decode(
        token,
        public_key.to_pem().decode(),
        algorithms=["RS256"],
        audience=EXPECTED_AUDIENCE,
        issuer=COGNITO_ISSUER
    )
    return claims