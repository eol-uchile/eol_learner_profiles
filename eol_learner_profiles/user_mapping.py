import csv
import io
import logging

from django.conf import settings

from .data_files import load_data_file
from .models import DataFile

logger = logging.getLogger(__name__)


def _parse_uid_mapping(text):
    """{user_id_staging: user_id_eol} desde el texto del CSV; ignora filas sin match (#N/A, vacío)."""
    mapping = {}
    dialect = csv.Sniffer().sniff(text[:2048], delimiters=',;')
    for row in csv.DictReader(io.StringIO(text), dialect=dialect):
        staging = (row.get('user_id_staging') or '').strip()
        prod = (row.get('user_id_eol') or '').strip()
        if not staging.isdigit() or not prod.isdigit():
            continue
        staging, prod = int(staging), int(prod)
        if mapping.get(staging, prod) != prod:
            logger.warning("uid staging %s mapeado a dos uid prod (%s, %s); se usa el primero", staging, mapping[staging], prod)
            continue
        mapping[staging] = prod
    return mapping

def get_api_uid(uid):
    """
    uid con el que se consulta la API. Con EOL_LEARNER_PROFILES_USE_UID_MAPPING
    activo traduce el uid de staging al de prod usando el último CSV subido en el
    admin (key uid_mapping). Si no hay CSV o el usuario no está en el mapeo
    devuelve None (no se consulta con su propio uid para no mostrar datos de otra persona).
    """
    use_mapping = str(getattr(settings, 'EOL_LEARNER_PROFILES_USE_UID_MAPPING', False)).lower() == 'true'
    if not use_mapping:
        return uid

    mapping = load_data_file(DataFile.UID_MAPPING, _parse_uid_mapping)
    if mapping is None:
        logger.warning("Mapeo de uid activo pero no hay CSV válido subido en el admin")
        return None

    return mapping.get(uid)
