import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CTLlavesAcceso")

def insertar(resultado):
    table.put_item(Item=resultado)