
"""Pruebas del administrador de temas de LibreSTRO."""

from theme_manager import aplicar_tema, cargar_temas


class SelectorSimulado:
    """Sustituye QComboBox durante las pruebas."""

    def __init__(self):
        self.elementos = []
        self.indice = -1
        self.habilitado = True

    def clear(self):
        self.elementos.clear()
        self.indice = -1

    def addItem(self, nombre, userData=None):
        self.elementos.append((nombre, userData))
        if self.indice == -1:
            self.indice = 0

    def setCurrentIndex(self, indice):
        self.indice = indice

    def currentData(self):
        if 0 <= self.indice < len(self.elementos):
            return self.elementos[self.indice][1]
        return None

    def setEnabled(self, habilitado):
        self.habilitado = habilitado


class ConfiguracionSimulada:
    """Almacena preferencias sin tocar QSettings real."""

    def __init__(self, tema="dark.qss"):
        self.datos = {"apariencia/tema": tema}

    def value(self, clave, predeterminado=None, type=None):
        return self.datos.get(clave, predeterminado)

    def setValue(self, clave, valor):
        self.datos[clave] = valor


class VentanaSimulada:
    """Recibe los estilos sin abrir una ventana gráfica."""

    def __init__(self):
        self.estilos = ""

    def setStyleSheet(self, estilos):
        self.estilos = estilos


def crear_tema(carpeta, nombre, contenido):
    archivo = carpeta / nombre
    archivo.write_text(contenido, encoding="utf-8")
    return archivo


def test_detectar_temas(tmp_path):
    crear_tema(tmp_path, "dark.qss", "QWidget { color: white; }")
    crear_tema(tmp_path, "light.qss", "QWidget { color: black; }")

    selector = SelectorSimulado()
    configuracion = ConfiguracionSimulada()

    cargar_temas(selector, tmp_path, configuracion, lambda: None)

    assert len(selector.elementos) == 2
    assert selector.currentData().name == "dark.qss"


def test_recuperar_tema_guardado(tmp_path):
    crear_tema(tmp_path, "dark.qss", "color: white;")
    crear_tema(tmp_path, "light.qss", "color: black;")

    selector = SelectorSimulado()
    configuracion = ConfiguracionSimulada("light.qss")

    cargar_temas(selector, tmp_path, configuracion, lambda: None)

    assert selector.currentData().name == "light.qss"


def test_tema_eliminado(tmp_path):
    crear_tema(tmp_path, "dark.qss", "color: white;")

    selector = SelectorSimulado()
    configuracion = ConfiguracionSimulada("inexistente.qss")

    cargar_temas(selector, tmp_path, configuracion, lambda: None)

    assert selector.currentData().name == "dark.qss"


def test_carpeta_vacia(tmp_path):
    selector = SelectorSimulado()
    configuracion = ConfiguracionSimulada()

    cargar_temas(selector, tmp_path, configuracion, lambda: None)

    assert selector.habilitado is False
    assert selector.currentData() is None


def test_aplicar_tema_y_guardar(tmp_path):
    crear_tema(tmp_path, "custom.qss", "QWidget { color: cyan; }")

    selector = SelectorSimulado()
    selector.addItem("Custom", userData=tmp_path / "custom.qss")

    ventana = VentanaSimulada()
    configuracion = ConfiguracionSimulada()

    aplicar_tema(selector, ventana, configuracion)

    assert "color: cyan" in ventana.estilos
    assert configuracion.value("apariencia/tema") == "custom.qss"
