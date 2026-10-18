"""LibreSTRO: ventana principal y coordinación de módulos."""

import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSettings, QStandardPaths
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from audio_player import ReproductorAudio
from theme_manager import aplicar_tema, cargar_temas
from ui_components import BarraLateral, BarraReproduccion, PanelBiblioteca


def formato_tiempo(milisegundos):
    segundos = max(0, milisegundos // 1000)
    minutos, segundos = divmod(segundos, 60)
    return f"{minutos}:{segundos:02d}"


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
        self.biblioteca = PanelBiblioteca()
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
        self.audio = ReproductorAudio(self)
        player = self.audio.reproductor
        self.biblioteca.boton_abrir.clicked.connect(self.abrir_archivo)
        self.controles.boton_reproducir.clicked.connect(self.audio.alternar_reproduccion)
        self.controles.volumen.valueChanged.connect(self.audio.fijar_volumen)
        self.controles.barra_progreso.sliderMoved.connect(player.setPosition)
        player.durationChanged.connect(self.actualizar_duracion)
        player.positionChanged.connect(self.actualizar_posicion)
        player.playbackStateChanged.connect(self.actualizar_boton)
        player.errorOccurred.connect(self.mostrar_error_audio)

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

        nombre = Path(ruta).name
        self.biblioteca.mensaje.setText(nombre)
        self.controles.cancion.setText(nombre)
        self.controles.cancion.setToolTip(ruta)
        self.audio.abrir(Path(ruta))

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
