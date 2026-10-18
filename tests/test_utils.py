
"""Pruebas de las funciones auxiliares de LibreSTRO."""

from utils import formato_tiempo


def test_tiempo_cero():
    assert formato_tiempo(0) == "0:00"


def test_tiempo_segundos():
    assert formato_tiempo(15000) == "0:15"


def test_tiempo_minutos():
    assert formato_tiempo(125000) == "2:05"


def test_tiempo_una_hora():
    assert formato_tiempo(3600000) == "60:00"


def test_tiempo_negativo():
    assert formato_tiempo(-1000) == "0:00"


def test_tiempo_milisegundos():
    assert formato_tiempo(1999) == "0:01"
