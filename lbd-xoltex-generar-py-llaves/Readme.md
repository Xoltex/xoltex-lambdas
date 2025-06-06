# Lambda: Generador de Llaves RSA y AES

Esta Lambda genera:
- Par de llaves RSA (pública/privada)
- Clave AES de 256 bits
- ID de acceso único (`idAcceso`)
- Expiración de 1 hora

Protegida por token JWT de Amazon Cognito.
