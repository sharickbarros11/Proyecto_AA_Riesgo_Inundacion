# Punto de entrada WSGI para PythonAnywhere.
# En el panel "Web" de PythonAnywhere, copia el contenido de la sección
# WSGI configuration file equivalente a esto (ajustando la ruta a tu usuario).

import sys

path = "/home/tu_usuario/floodapp"  # <-- cambia "tu_usuario"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application  # noqa: E402
