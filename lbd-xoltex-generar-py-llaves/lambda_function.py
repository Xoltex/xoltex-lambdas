from excepciones.errores import manejar_errores
from utilidades.folio_context import generar_nuevo_folio
from respuestas.AppResponse import AppResponse
from funciones.index import funcion
from pydantic import ValidationError
from esquema.validarRequest import HeadersSchema,PathParamsSchema,BodySchema
from excepciones.errores import AppError


@manejar_errores
def lambda_handler(event, context):
    generar_nuevo_folio()
    try:
        pass
        #headers = HeadersSchema(**event.get("headers", {}))
        # path_params = PathParamsSchema(**event.get("pathParameters", {}))
        # body = BodySchema(**json.loads(event.get("body", "{}")))
  
    except ValidationError as e:
        print(e.errors())  
        raise AppError(404, "Parametros no validos")
         
    
    path_params = event.get("pathParameters") or {}
    response= funcion.crearLLaves(path_params,event)
    return AppResponse.ok(response)
 
