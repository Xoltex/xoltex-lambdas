from utilidades.folio_context import obtener_folio
import traceback
import json
from typing import Optional, Callable, Any, Dict
from fastapi.responses import JSONResponse

class AppError(Exception):
    _mensajes_por_codigo = {
        400: "Solicitud inválida",
        401: "No autenticado",
        403: "Acceso denegado",
        404: "Recurso no encontrado",
        422: "Entidad no procesable",
        500: "Error interno del servidor",
        502: "Error de puerta de enlace",
        503: "Servicio no disponible"
    }

    def __init__(self, status: int = 400, detalle: Optional[str] = None, mensaje: Optional[str] = None, causa: Optional[Exception] = None):
        super().__init__(mensaje)
        self.folio = str(obtener_folio())
        self.status = status
        self.mensaje = mensaje or self._mensajes_por_codigo.get(status, "Error desconocido")
        self.detalle = detalle or (str(causa) if causa else "Sin detalles técnicos.")
        self.causa = causa
        self.trace = traceback.format_exc() if causa else None

    def to_dict(self, incluir_trace: bool = False) -> Dict[str, Any]:
        data = {
            "mensaje": self.mensaje,
            "folio": self.folio,
            "estatus": self.status,
            "error": self.detalle
        }
        if incluir_trace and self.trace:
            data["traceback"] = self.trace
        return data

class ErrorManager:
    @staticmethod
    def capturar(ex: Exception, default_status: int = 500, incluir_trace: bool = True) -> Dict[str, Any]:
        if isinstance(ex, AppError):
            return ex.to_dict(incluir_trace=incluir_trace)
        else:
            return {
                "mensaje": "Error inesperado",
                "folio": str(obtener_folio()),
                "estatus": default_status,
                "error": str(ex),
                "traceback": traceback.format_exc() if incluir_trace else None
            }


def manejar_errores(func: Callable) -> Callable:
    def wrapper(*args, **kwargs) -> Any:
        try:
            result = func(*args, **kwargs)

            if isinstance(result, JSONResponse):
                return result

            if isinstance(result, dict) and "statusCode" in result and "body" in result:
                return result

            if isinstance(result, dict):
                return JSONResponse(content=result, status_code=200)

            return JSONResponse(content={"mensaje": "Resultado inesperado", "resultado": str(result)}, status_code=200)

        except AppError as e:
            return _responder(e.to_dict(), e.status, args)

        except Exception as e:
            error_dict = ErrorManager.capturar(e)
            return _responder(error_dict, error_dict["estatus"], args)

    def _responder(error_dict: dict, status_code: int, args) -> Any:
        if len(args) == 2 and isinstance(args[0], dict) and isinstance(args[1], object):
            return {
                "statusCode": status_code,
                "body": json.dumps(error_dict)
            }
        else:
            return JSONResponse(content=error_dict, status_code=status_code)
    

    return wrapper
