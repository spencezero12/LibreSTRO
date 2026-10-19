"""Pruebas de la cola secuencial de LibreSTRO."""

from pathlib import Path

import pytest

from playback_queue import ColaReproduccion


def test_cola_vacia():
    cola = ColaReproduccion()
    assert cola.actual is None
    assert cola.siguiente() is None
    assert cola.anterior() is None


def test_cargar_y_avanzar():
    cola = ColaReproduccion()
    pistas = [Path("a.mp3"), Path("b.flac"), Path("c.ogg")]
    assert cola.cargar(pistas) == pistas[0]
    assert cola.siguiente() == pistas[1]
    assert cola.siguiente() == pistas[2]
    assert cola.siguiente() is None
    assert cola.actual == pistas[2]


def test_retroceder_sin_saltar_inicio():
    cola = ColaReproduccion()
    pistas = [Path("a.mp3"), Path("b.mp3")]
    cola.cargar(pistas, inicio=1)
    assert cola.anterior() == pistas[0]
    assert cola.anterior() is None
    assert cola.actual == pistas[0]


def test_reemplazar_por_cola_vacia():
    cola = ColaReproduccion()
    cola.cargar([Path("a.mp3")])
    assert cola.cargar([]) is None
    assert cola.actual is None
    assert cola.indice == -1


def test_indice_invalido_no_cambia_cola():
    cola = ColaReproduccion()
    cola.cargar([Path("anterior.mp3")])
    with pytest.raises(IndexError):
        cola.cargar([Path("nueva.mp3")], inicio=3)
    assert cola.actual == Path("anterior.mp3")


def test_inicio_en_segunda_pista():
    cola = ColaReproduccion()
    pistas = [Path("a.mp3"), Path("b.mp3"), Path("c.mp3")]
    assert cola.cargar(pistas, inicio=1) == pistas[1]
    assert cola.anterior() == pistas[0]
