# Python Hello

El boilerplate más básico para comenzar un proyecto en Python en 4Geeks. Inicia tu primer proyecto en Python desde cero.

## Cómo ejecutar el proyecto

Para iniciar el Asistente de Inventario con IA, debes ejecutar tanto la API como el Agente en dos terminales separados.

1. **Terminal 1 - Arrancar la API**:
```bash
uvicorn api.app:app --reload
```
Asegúrate de que la API esté en ejecución antes de iniciar el agente.

2. **Terminal 2 - Arrancar el Agente**:
```bash
python agent.py
```

Puedes crear e incluir tantos archivos de Python (también conocidos como módulos) como desees utilizando las declaraciones de importación.

## Requisitos

Asegúrate de tener Python instalado en tu computadora. Te recomendamos encarecidamente [instalar Python a través de Pyenv](https://4geeks.com/es/how-to/que-es-pyenv-y-como-instalar-pyenv) para evitar conflictos de versiones en el futuro.

### Contribuidores

Esta plantilla fue creada como parte de los [Recursos de Python de 4Geeks](https://4geeks.com/es/technology/python) para el aprendizaje en [4Geeks.com](https://4geeks.com) por [Alejandro Sanchez](https://twitter.com/alesanchezr) y [muchos otros contribuyentes](https://github.com/4GeeksAcademy/python-hello/graphs/contributors).
