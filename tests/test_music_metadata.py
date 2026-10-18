
"""Pruebas de metadatos musicales de LibreSTRO."""

from types import SimpleNamespace

import pytest

import music_library
from music_library import leer_metadatos


def test_archivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        leer_metadatos(tmp_path / "inexistente.mp3")


def test_archivo_sin_etiquetas(tmp_path, monkeypatch):
    ruta = tmp_path / "cancion.mp3"
    ruta.write_bytes(b"")

    monkeypatch.setattr(
        music_library,
        "File",
        lambda ruta, easy=True: None,
    )

    cancion = leer_metadatos(ruta)

    assert cancion.titulo == "cancion"
    assert cancion.artista == "Artista desconocido"
    assert cancion.album == "Álbum desconocido"
    assert cancion.duracion == 0.0


def test_metadatos_validos(tmp_path, monkeypatch):
    ruta = tmp_path / "ejemplo.flac"
    ruta.write_bytes(b"")

    class AudioSimulado(dict):
        info = SimpleNamespace(length=125.5)

    audio = AudioSimulado({
        "title": ["Canción de prueba"],
        "artist": ["Artista de prueba"],
        "album": ["Álbum de prueba"],
    })

    monkeypatch.setattr(
        music_library,
        "File",
        lambda ruta, easy=True: audio,
    )

    cancion = leer_metadatos(ruta)

    assert cancion.titulo == "Canción de prueba"
    assert cancion.artista == "Artista de prueba"
    assert cancion.album == "Álbum de prueba"
    assert cancion.duracion == 125.5


def test_archivo_no_modificado(tmp_path):
    ruta = tmp_path / "prueba.mp3"
    contenido = b"contenido de prueba"
    ruta.write_bytes(contenido)

    leer_metadatos(ruta)

    assert ruta.read_bytes() == contenido
