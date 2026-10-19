"""LibreSTRO: ventana principal y coordinación de módulos."""

import sys
from pathlib import Path

from PySide6.QtCore import QSettings, QStandardPaths, Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from audio_player import ReproductorAudio
from library_panel import PanelBibliotecaMusical
from playback_queue import ColaReproduccion
from theme_manager import aplicar_tema, cargar_temas
from ui_components import BarraLateral, BarraReproduccion
from utils import formato_tiempo


class LibreSTRO(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LibreSTRO")
        self.resize(1000, 650)
        self.setMinimumSize(700, 450)

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setSpacing(10)

        encabezado_layout = QHBoxLayout()
        titulo = QLabel("LibreSTRO")
        titulo.setObjectName("titulo")
        self.selector_temas = QComboBox()
        self.selector_temas.setToolTip("Seleccionar apariencia de LibreSTRO")
        self.selector_temas.setMinimumWidth(160)
        encabezado_layout.addWidget(titulo)
        encabezado_layout.addStretch()
        encabezado_layout.addWidget(self.selector_temas)
        layout_principal.addLayout(encabezado_layout)

        contenido = QHBoxLayout()
        contenido.setSpacing(10)
        self.barra_lateral = BarraLateral()
        self.biblioteca = PanelBibliotecaMusical()
        contenido.addWidget(self.barra_lateral)
        contenido.addWidget(self.biblioteca, 1)
        layout_principal.addLayout(contenido, 1)

        self.controles = BarraReproduccion()
        layout_principal.addWidget(self.controles)

        # Paso 12: conservar el administrador de temas existente.
        self.directorio_temas = Path(__file__).resolve().parent / "themes"
        self.configuracion = QSettings("LibreSTRO", "LibreSTRO")
        self.cargar_temas()
        self.selector_temas.currentIndexChanged.connect(self.cambiar_tema)

        # Paso 14: servicio de audio independiente de la interfaz.
        self.cola = ColaReproduccion()
        self.audio = ReproductorAudio(self)
        player = self.audio.reproductor
        self.biblioteca.boton_abrir.clicked.connect(self.abrir_archivo)
        self.biblioteca.cancion_elegida.connect(self.reproducir_cancion_biblioteca)
        self.controles.boton_reproducir.clicked.connect(self.audio.alternar_reproduccion)
        self.controles.boton_anterior.clicked.connect(self.reproducir_anterior)
        self.controles.boton_siguiente.clicked.connect(self.reproducir_siguiente)
        self.controles.volumen.valueChanged.connect(self.audio.fijar_volumen)
        self.controles.barra_progreso.sliderMoved.connect(player.setPosition)
        player.durationChanged.connect(self.actualizar_duracion)
        player.positionChanged.connect(self.actualizar_posicion)
        player.playbackStateChanged.connect(self.actualizar_boton)
        player.errorOccurred.connect(self.mostrar_error_audio)
        player.mediaStatusChanged.connect(self._comprobar_fin_de_pista)

    def cargar_temas(self):
        cargar_temas(
            self.selector_temas,
            self.directorio_temas,
            self.configuracion,
            self.cambiar_tema,
        )

    def cambiar_tema(self, indice=None):
        aplicar_tema(self.selector_temas, self, self.configuracion)

    def abrir_archivo(self):
        carpeta_musica = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.MusicLocation
        )
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de audio",
            carpeta_musica or str(Path.home()),
            "Archivos de audio (*.mp3 *.wav *.flac *.ogg *.m4a);;Todos los archivos (*)",
        )
        if not ruta:
            return

        # Archivo individual: cola de una sola canción.
        self.cola.cargar([Path(ruta)])
        self._reproducir_actual()

    def reproducir_cancion_biblioteca(self, ruta):
        """Construir una cola con el orden actual de las filas de la tabla."""
        archivo = Path(ruta)
        if not archivo.is_file():
            QMessageBox.warning(self, "Archivo no disponible", str(archivo))
            return

        rutas = []
        for fila in range(self.biblioteca.tabla.rowCount()):
            celda = self.biblioteca.tabla.item(fila, 0)
            if celda is None:
                continue
            valor = celda.data(Qt.ItemDataRole.UserRole)
            if valor:
                rutas.append(Path(valor))

        # Una pista puede haberse añadido mientras todavía se escanea.
        if archivo not in rutas:
            rutas.append(archivo)
        indice = rutas.index(archivo)
        self.cola.cargar(rutas, indice)
        self._reproducir_actual()

    def _reproducir_actual(self):
        """Abrir la pista seleccionada sin cambiar el orden de la cola."""
        ruta = self.cola.actual
        if ruta is None:
            return
        if not ruta.is_file():
            QMessageBox.warning(self, "Archivo no disponible", str(ruta))
            return
        self.biblioteca.mensaje.setText(ruta.name)
        self.controles.cancion.setText(ruta.name)
        self.controles.cancion.setToolTip(str(ruta))
        self.audio.abrir(ruta)

    def reproducir_siguiente(self):
        """Saltar a la siguiente pista, si existe."""
        if self.cola.siguiente() is not None:
            self._reproducir_actual()

    def reproducir_anterior(self):
        """Volver a la pista previa, si existe."""
        if self.cola.anterior() is not None:
            self._reproducir_actual()

    def _comprobar_fin_de_pista(self, estado):
        """Continuar automáticamente solo al terminar el archivo."""
        if estado == QMediaPlayer.MediaStatus.EndOfMedia:
            self.reproducir_siguiente()

    def closeEvent(self, evento):
        self.biblioteca.detener_escaneo()
        super().closeEvent(evento)

    def actualizar_duracion(self, duracion):
        self.controles.barra_progreso.setRange(0, max(0, duracion))
        self.controles.duracion.setText(formato_tiempo(duracion))

    def actualizar_posicion(self, posicion):
        if not self.controles.barra_progreso.isSliderDown():
            self.controles.barra_progreso.setValue(posicion)
        self.controles.tiempo_actual.setText(formato_tiempo(posicion))

    def actualizar_boton(self, estado):
        if estado == QMediaPlayer.PlaybackState.PlayingState:
            self.controles.boton_reproducir.setText("⏸")
        else:
            self.controles.boton_reproducir.setText("▶")

    def mostrar_error_audio(self, error, descripcion):
        if error != QMediaPlayer.Error.NoError:
            QMessageBox.warning(
                self,
                "Error de reproducción",
                descripcion or "No se pudo reproducir el archivo.",
            )


def main():
    app = QApplication(sys.argv)
    ventana = LibreSTRO()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
