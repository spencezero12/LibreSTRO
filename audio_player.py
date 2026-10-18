"""Servicio de reproducción de audio local de LibreSTRO."""

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer


class ReproductorAudio(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.salida = QAudioOutput(self)
        self.reproductor = QMediaPlayer(self)
        self.reproductor.setAudioOutput(self.salida)
        self.salida.setVolume(0.7)

    def abrir(self, ruta):
        self.reproductor.setSource(QUrl.fromLocalFile(str(ruta)))
        self.reproductor.play()

    def alternar_reproduccion(self):
        if not self.reproductor.source().isValid():
            return
        if self.reproductor.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.reproductor.pause()
        else:
            self.reproductor.play()

    def fijar_volumen(self, valor):
        self.salida.setVolume(valor / 100.0)
