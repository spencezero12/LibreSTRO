"""Componentes visuales reutilizables de LibreSTRO."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)


class BarraLateral(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("barraLateral")
        self.setFixedWidth(180)

        menu = QVBoxLayout(self)
        self.boton_biblioteca = QPushButton("Biblioteca")
        menu.addWidget(self.boton_biblioteca)

        # Estas vistas se implementarán más adelante.
        for nombre in ("Listas", "En línea", "Ajustes"):
            boton = QPushButton(nombre)
            boton.setEnabled(False)
            boton.setToolTip("Disponible en una versión futura")
            menu.addWidget(boton)
        menu.addStretch()


class PanelBiblioteca(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("biblioteca")
        layout = QVBoxLayout(self)

        titulo = QLabel("Tu biblioteca musical")
        titulo.setObjectName("encabezado")
        layout.addWidget(titulo)

        self.mensaje = QLabel("Selecciona un archivo para comenzar.")
        self.mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mensaje.setWordWrap(True)

        self.boton_abrir = QPushButton("Abrir archivo de audio…")
        self.boton_abrir.setToolTip("Seleccionar un archivo local")

        layout.addStretch()
        layout.addWidget(self.mensaje)
        layout.addWidget(self.boton_abrir, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()


class BarraReproduccion(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("reproductor")
        layout = QVBoxLayout(self)

        fila = QHBoxLayout()
        self.cancion = QLabel("Sin reproducción")
        self.cancion.setMinimumWidth(130)
        fila.addWidget(self.cancion, 1)

        self.boton_reproducir = QPushButton("▶")
        self.boton_reproducir.setToolTip("Reproducir / pausar")
        fila.addWidget(self.boton_reproducir)

        self.volumen = QSlider(Qt.Orientation.Horizontal)
        self.volumen.setRange(0, 100)
        self.volumen.setValue(70)
        self.volumen.setFixedWidth(110)
        self.volumen.setToolTip("Volumen")
        fila.addWidget(QLabel("Volumen"))
        fila.addWidget(self.volumen)
        layout.addLayout(fila)

        progreso = QHBoxLayout()
        self.tiempo_actual = QLabel("0:00")
        self.barra_progreso = QSlider(Qt.Orientation.Horizontal)
        self.barra_progreso.setRange(0, 0)
        self.barra_progreso.setToolTip("Posición de reproducción")
        self.duracion = QLabel("0:00")
        progreso.addWidget(self.tiempo_actual)
        progreso.addWidget(self.barra_progreso, 1)
        progreso.addWidget(self.duracion)
        layout.addLayout(progreso)
