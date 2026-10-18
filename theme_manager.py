
# LibreSTRO - Administrador de temas


def cargar_temas(selector, directorio, configuracion, aplicar):
    """Detectar temas y restaurar el último utilizado."""

    selector.clear()

    archivos = sorted(directorio.glob("*.qss"))

    for archivo in archivos:
        nombre = archivo.stem.replace("_", " ").title()
        selector.addItem(nombre, userData=archivo)

    if not archivos:
        print("No se encontraron temas en themes/")
        selector.setEnabled(False)
        return

    selector.setEnabled(True)

    tema_guardado = configuracion.value(
        "apariencia/tema",
        "dark.qss",
        type=str
    )

    nombres = [archivo.name for archivo in archivos]

    if tema_guardado in nombres:
        indice = nombres.index(tema_guardado)
    elif "dark.qss" in nombres:
        indice = nombres.index("dark.qss")
    else:
        indice = 0

    selector.setCurrentIndex(indice)
    aplicar()


def aplicar_tema(selector, ventana, configuracion):
    """Aplicar el tema seleccionado y guardar la preferencia."""

    archivo = selector.currentData()

    if archivo is None:
        return

    try:
        estilos = archivo.read_text(encoding="utf-8")

        ventana.setStyleSheet(estilos)

        configuracion.setValue(
            "apariencia/tema",
            archivo.name
        )

    except (OSError, UnicodeError) as error:
        print(f"Error al cargar el tema: {error}")
