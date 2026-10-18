
"""Funciones auxiliares de LibreSTRO."""


def formato_tiempo(milisegundos: int) -> str:
    """Convertir milisegundos al formato minutos:segundos."""
    segundos = max(0, milisegundos // 1000)
    minutos, segundos = divmod(segundos, 60)

    return f"{minutos}:{segundos:02d}"
