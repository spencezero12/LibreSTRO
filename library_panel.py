"""Panel de biblioteca: selección de carpetas y escaneo no bloqueante."""

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from music_library import buscar_archivos_musicales, leer_metadatos
from utils import formato_tiempo


class ExploradorMusical(QThread):
    """Lee archivos fuera del hilo de la interfaz gráfica."""

    encontrado = Signal(object)
    fallo = Signal(str)

    def __init__(self, carpeta: Path, parent=None):
        super().__init__(parent)
        self.carpeta = carpeta

    def run(self):
        try:
            for ruta in buscar_archivos_musicales(self.carpeta):
                if self.isInterruptionRequested():
                    break
                try:
                    cancion = leer_metadatos(ruta)
                except (OSError, ValueError, TypeError) as error:
                    self.fallo.emit(f"No se pudo leer {ruta.name}: {error}")
                    continue
                self.encontrado.emit(cancion)
        except (OSError, ValueError) as error:
            self.fallo.emit(str(error))


class PanelBibliotecaMusical(QFrame):
    """Tabla de canciones y botones para abrir archivos o carpetas."""

    cancion_elegida = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("biblioteca")
        self._explorador = None
        self._cantidad = 0

        layout = QVBoxLayout(self)
        titulo = QLabel("Tu biblioteca musical")
        titulo.setObjectName("encabezado")
        layout.addWidget(titulo)

        botones = QHBoxLayout()
        self.boton_abrir = QPushButton("Abrir archivo…")
        self.boton_carpeta = QPushButton("Añadir carpeta…")
        botones.addWidget(self.boton_abrir)
        botones.addWidget(self.boton_carpeta)
        layout.addLayout(botones)

        self.mensaje = QLabel("Selecciona una carpeta para encontrar música.")
        layout.addWidget(self.mensaje)

        self.tabla = QTableWidget(0, 4)
        self.tabla.setHorizontalHeaderLabels(
            ["Título", "Artista", "Álbum", "Duración"]
        )
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.cellDoubleClicked.connect(self._abrir_fila)
        layout.addWidget(self.tabla, 1)
        self.boton_carpeta.clicked.connect(self.elegir_carpeta)

    def elegir_carpeta(self):
        if self._explorador is not None and self._explorador.isRunning():
            return
        carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta musical", str(Path.home())
        )
        if carpeta:
            self.escanear(Path(carpeta))

    def escanear(self, carpeta: Path):
        if self._explorador is not None and self._explorador.isRunning():
            return
        self.tabla.setRowCount(0)
        self._cantidad = 0
        self.boton_carpeta.setEnabled(False)
        self.mensaje.setText("Buscando canciones…")
        self._explorador = ExploradorMusical(carpeta, self)
        self._explorador.encontrado.connect(self._agregar_cancion)
        self._explorador.fallo.connect(self._mostrar_error)
        self._explorador.finished.connect(self._finalizar)
        self._explorador.start()

    def _agregar_cancion(self, cancion):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)
        datos = (
            cancion.titulo,
            cancion.artista,
            cancion.album,
            formato_tiempo(int(cancion.duracion * 1000)),
        )
        for columna, valor in enumerate(datos):
            celda = QTableWidgetItem(valor)
            if columna == 0:
                celda.setData(Qt.ItemDataRole.UserRole, str(cancion.ruta))
                celda.setToolTip(str(cancion.ruta))
            self.tabla.setItem(fila, columna, celda)
        self._cantidad += 1

    def _mostrar_error(self, mensaje):
        self.mensaje.setText(f"Aviso: {mensaje}")

    def _finalizar(self):
        self.boton_carpeta.setEnabled(True)
        self.mensaje.setText(f"{self._cantidad} canciones encontradas")

    def _abrir_fila(self, fila, _columna):
        celda = self.tabla.item(fila, 0)
        if celda is not None:
            ruta = celda.data(Qt.ItemDataRole.UserRole)
            if ruta:
                self.cancion_elegida.emit(ruta)

    def detener_escaneo(self):
        if self._explorador is not None and self._explorador.isRunning():
            self._explorador.requestInterruption()
            self._explorador.wait()
