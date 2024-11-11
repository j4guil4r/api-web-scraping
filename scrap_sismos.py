import requests
import boto3
import uuid

def lambda_handler(event, context):
    # URL de la API de sismos
    url = "https://ultimosismo.igp.gob.pe/api/ultimo-sismo/ajaxb/2024"

    # Realizar la solicitud HTTP a la API
    response = requests.get(url)
    if response.status_code != 200:
        return {
            'statusCode': response.status_code,
            'body': 'Error al acceder a la API de sismos'
        }

    # Parsear el contenido JSON de la respuesta
    sismos = response.json()

    # Extraer los primeros 10 sismos
    primeros_10_sismos = sismos[:10]

    # Guardar los datos en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TablaSismos')

    # Eliminar todos los elementos de la tabla antes de agregar los nuevos
    scan = table.scan()
    with table.batch_writer() as batch:
        for each in scan['Items']:
            batch.delete_item(
                Key={
                    'id': each['id']
                }
            )

    # Insertar los nuevos datos
    for sismo in primeros_10_sismos:
        sismo['id'] = str(uuid.uuid4())  # Generar un ID único para cada entrada
        table.put_item(Item=sismo)

    # Retornar el resultado como JSON
    return {
        'statusCode': 200,
        'body': primeros_10_sismos
    }
