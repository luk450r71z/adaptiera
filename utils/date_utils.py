from datetime import datetime, timedelta
from typing import Optional

def format_date(date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Formatea una fecha según el formato especificado."""
    return date.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parsea una cadena de fecha según el formato especificado."""
    return datetime.strptime(date_str, format_str)

def get_time_ago(date: datetime) -> str:
    """Retorna una descripción de cuánto tiempo ha pasado desde la fecha dada."""
    now = datetime.now()
    diff = now - date

    if diff < timedelta(minutes=1):
        return "hace un momento"
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f"hace {minutes} minutos"
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f"hace {hours} horas"
    elif diff < timedelta(days=30):
        days = diff.days
        return f"hace {days} días"
    else:
        return format_date(date) 
        

def fecha_actual():
    return datetime.now().strftime("%Y-%m-%d")
