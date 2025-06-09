from utilidades.folio_context import obtener_folio
from typing import Any, Dict, Optional, Union, List


class AppResponse:
    """
    Clase para generar respuestas exitosas estandarizadas: 200 OK y 201 Created.
    """

    @staticmethod
    def ok(
        resultado: Union[Dict, List],
        mensaje: str = "Operación exitosa",
        extra: Optional[dict] = None
    ) -> Dict:
        return AppResponse._crear_respuesta(200, resultado, mensaje, extra)

    @staticmethod
    def created(
        resultado: Union[Dict, List],
        mensaje: str = "Recurso creado exitosamente",
        extra: Optional[dict] = None
    ) -> Dict:
        return AppResponse._crear_respuesta(201, resultado, mensaje, extra)

    @staticmethod
    def _crear_respuesta(
        status: int,
        resultado: Union[Dict, List],
        mensaje: str,
        extra: Optional[dict] = None
    ) -> Dict:
        respuesta = {
            "mensaje": mensaje,
            "folio": str(obtener_folio()),
            "estatus": status,
            "resultado": resultado
        }
        if extra:
            respuesta["extra"] = extra
        return respuesta
