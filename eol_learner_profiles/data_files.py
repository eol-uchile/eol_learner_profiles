import logging

logger = logging.getLogger(__name__)

_CACHE = {}

def load_data_file(key, parse):
    """
    Contenido parseado del último DataFile subido con ``key``, o None si no hay
    o falla la lectura. ``parse`` recibe el texto del archivo. Se reparsea solo
    cuando se sube un archivo nuevo para esa key.
    """
    try:
        from .models import DataFile
        latest = DataFile.objects.filter(key=key).order_by('-uploaded_at').first()
    except Exception as e:
        logger.error("Error consultando DataFile %s: %s", key, str(e))
        return None

    if latest is None:
        return None

    cached = _CACHE.get(key)
    if cached and cached[0] == latest.pk:
        return cached[1]

    try:
        with latest.file.open('rb') as f:
            data = parse(f.read().decode('utf-8-sig'))
    except Exception as e:
        logger.error("Error leyendo DataFile %s (%s): %s", key, latest.file.name, str(e))
        return None

    _CACHE[key] = (latest.pk, data)
    logger.info("DataFile %s cargado desde %s", key, latest.file.name)
    return data
