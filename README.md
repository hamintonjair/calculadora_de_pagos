# Calculadora de Pagos de Contratos

Una aplicación web para calcular pagos de contratos con sistema de autenticación y base de datos MongoDB.

## Características

- Sistema de autenticación de usuarios
- Registro de usuarios con datos personales
- Cálculo de pagos de contratos
- Interfaz moderna y responsiva
- Almacenamiento de datos en MongoDB Atlas

## Requisitos

- Python 3.8 o superior
- MongoDB Atlas (cuenta gratuita)
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:

```bash
git clone <url-del-repositorio>
cd calculadora
```

2. Crear un entorno virtual:

```bash
python -m venv venv
```

3. Activar el entorno virtual:

- Windows:

```bash
venv\Scripts\activate
```

- Linux/Mac:

```bash
source venv/bin/activate
```

4. Instalar dependencias:

```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:

- Crear un archivo `.env` en la raíz del proyecto
- Agregar la siguiente línea con tu URL de conexión de MongoDB:

```
MONGODB_URI=mongodb+srv://<usuario>:<contraseña>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

6. Configurar la estructura del proyecto:

```bash
python setup.py
```

## Uso

1. Iniciar el servidor:

```bash
python app.py
```

2. Abrir el navegador y acceder a:

```
http://localhost:5000
```

3. Registrar un nuevo usuario o iniciar sesión con uno existente.

4. Usar la calculadora para calcular pagos de contratos.

## Estructura del Proyecto

```
calculadora/
├── app.py              # Aplicación principal
├── requirements.txt    # Dependencias
├── setup.py           # Script de configuración
├── .env              # Variables de entorno
├── templates/        # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── registro.html
│   ├── calculadora.html
│   └── actualizar_perfil.html
└── static/          # Archivos estáticos
    ├── css/
    └── js/
```

## Seguridad

- Las contraseñas se almacenan hasheadas
- Las rutas están protegidas con autenticación
- Se utilizan variables de entorno para datos sensibles

## Contribuir

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
