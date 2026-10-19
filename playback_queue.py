"""Cola secuencial de pistas, independiente de Qt."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ColaReproduccion:
    """Mantiene una lista de archivos y un índice seleccionado."""

    canciones: list[Path] = field(default_factory=list)
    indice: int = -1

    @property
    def actual(self) -> Path | None:
        if 0 <= self.indice < len(self.canciones):
            return self.canciones[self.indice]
        return None

    def cargar(self, rutas: list[Path], inicio: int = 0) -> Path | None:
        """Sustituye la cola y selecciona una pista."""
        canciones = [Path(ruta) for ruta in rutas]
        if not canciones:
            self.canciones = []
            self.indice = -1
            return None
        if not 0 <= inicio < len(canciones):
            raise IndexError("Índice inicial fuera de la cola")
        self.canciones = canciones
        self.indice = inicio
        return self.actual

    def siguiente(self) -> Path | None:
        """Avanza sin repetir al llegar al final."""
        if self.indice < 0 or self.indice + 1 >= len(self.canciones):
            return None
        self.indice += 1
        return self.actual

    def anterior(self) -> Path | None:
        """Retrocede sin repetir al llegar al inicio."""
        if self.indice <= 0:
            return None
        self.indice -= 1
        return self.actual
