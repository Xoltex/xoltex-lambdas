import uuid
import contextvars

# Variable de contexto para esta ejecución
_folio_actual: contextvars.ContextVar[str] = contextvars.ContextVar("folio", default=None)

def generar_nuevo_folio() -> str:
    folio = str(uuid.uuid4())
    _folio_actual.set(folio)
    return folio

def obtener_folio() -> str:
    folio = _folio_actual.get()
    if folio is None:
        return generar_nuevo_folio()
    return folio
