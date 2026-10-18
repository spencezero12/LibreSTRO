
"""LibreSTRO: gestión de archivos musicales locales."""

import os
from dataclasses import dataclass
from pathlib import Path

from mutagen import File, MutagenError

EXTENSIONES_AUDIO = frozenset({
    ".mp3",
    ".flac",
    ".ogg",
    ".opus",
    ".wav",
    ".m4a",
})


@dataclass(frozen=True, slots=True)
class Cancion:
    """Metadatos de un archivo musical."""

    ruta: Path
    titulo: str
    artista: str
    album: str
    duracion: float


def buscar_archivos_musicales(carpeta: Path) -> list[Path]:
    """Buscar archivos de audio sin modificarlos."""

    carpeta = Path(carpeta).expanduser()

    if not carpeta.is_dir():
        raise NotADirectoryError(
            f"La carpeta no existe o no es válida: {carpeta}"
        )

    archivos_encontrados = []

    def informar_error(error):
        print(f"No se pudo acceder a una carpeta: {error}")

    for raiz, directorios, archivos in os.walk(
        carpeta,
        followlinks=False,
        onerror=informar_error,
    ):
        # Evitar entrar a directorios enlazados
        directorios[:] = [
            nombre
            for nombre in directorios
            if not (Path(raiz) / nombre).is_symlink()
        ]

        for nombre in archivos:
            ruta = Path(raiz) / nombre

            if ruta.is_symlink():
                continue

            if ruta.suffix.lower() in EXTENSIONES_AUDIO:
                archivos_encontrados.append(ruta)

    return sorted(
        archivos_encontrados,
        key=lambda ruta: str(ruta).casefold(),
    )


def obtener_etiqueta(audio, nombre: str, predeterminado: str) -> str:
    """Leer una etiqueta o devolver un valor predeterminado."""

    valores = audio.get(nombre)

    if not valores:
        return predeterminado

    valor = valores[0] if isinstance(valores, (list, tuple)) else valores
    texto = str(valor).strip()

    return texto or predeterminado


def leer_metadatos(ruta: Path) -> Cancion:
    """Leer información musical sin modificar el archivo."""

    ruta = Path(ruta)

    if not ruta.is_file():
        raise FileNotFoundError(ruta)

    titulo = ruta.stem
    artista = "Artista desconocido"
    album = "Álbum desconocido"
    duracion = 0.0

    try:
        audio = File(ruta, easy=True)

        if audio is not None:
            titulo = obtener_etiqueta(audio, "title", titulo)
            artista = obtener_etiqueta(audio, "artist", artista)
            album = obtener_etiqueta(audio, "album", album)

            info = getattr(audio, "info", None)

            if info is not None:
                duracion = max(
                    0.0,
                    float(getattr(info, "length", 0) or 0),
                )

    except (MutagenError, OSError, ValueError, TypeError):
        # Una etiqueta dañada no debe detener la biblioteca.
        pass

    return Cancion(
        ruta=ruta,
        titulo=titulo,
        artista=artista,
        album=album,
        duracion=duracion,
    )
