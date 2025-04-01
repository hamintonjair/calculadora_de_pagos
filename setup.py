import os
import shutil

def crear_estructura():
    # Crear directorios
    directorios = [
        'templates',
        'static',
        'static/css',
        'static/js'
    ]
    
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
    
    # Mover archivos
    archivos = {
        'index.html': 'templates/calculadora.html',
        'static/css/styles.css': 'static/css/styles.css',
        'static/js/script.js': 'static/js/script.js'
    }
    
    for origen, destino in archivos.items():
        if os.path.exists(origen):
            shutil.copy2(origen, destino)

if __name__ == '__main__':
    crear_estructura()
    print("Estructura de directorios creada exitosamente.") 