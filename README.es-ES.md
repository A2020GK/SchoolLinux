# SchoolLinux

Plataforma educativa interactiva para practicar comandos de Linux en formato de taller lúdico en un aula de informática.

---

## Contenido

1. [Descripción breve](#1-descripción-breve)
2. [Guía de instalación](#2-guía-de-instalación)
3. [Guía para la creación de juegos personalizados](#3-guía-para-la-creación-de-juegos-personalizados)
4. [Diferencias respecto a la v2](#4-diferencias-respecto-a-la-v2)
5. [Arquitectura y estructura del proyecto](#arquitectura-y-estructura-del-proyecto)
6. [API y eventos en tiempo real](#api-y-eventos-en-tiempo-real)
7. [CI/CD y archivo de lanzamiento](#cicd-y-archivo-de-lanzamiento)
8. [Limitaciones y recomendaciones prácticas](#limitaciones-y-recomendaciones-prácticas)

---

## 1. Descripción breve

SchoolLinux ayuda al profesor a realizar sesiones prácticas sobre la terminal de Linux en forma de juegos.

Cómo funciona:

- Los alumnos se registran a través de una interfaz web.
- El profesor elige un juego e inicia la ronda.
- El Backend despliega tareas individuales en las máquinas de los alumnos vía SSH.
- Los alumnos buscan "tesoros" (o cumplen otras condiciones del juego) en la terminal de Linux.
- El progreso y los puntos son visibles para el profesor en tiempo real.

Características clave de la versión actual:

- Sistema de juegos basado en plugins (`backend/app/games/*.py`).
- FastAPI + Socket.IO (ASGI) para REST y actualizaciones en tiempo real.
- Estado tipado y persistencia JSON en `SLData.json`.
- Frontend en React + TypeScript con pantallas independientes para el profesor y el alumno.
- Pruebas de backend (`pytest`) y pipelines de CI para testing y construcción.

---

## 2. Guía de instalación

### 2.1 Instalación de Release

Si necesita un archivo listo para usar sin compilar desde el código fuente:

1. Abra la página de GitHub Releases del proyecto.
2. Descargue el archivo de lanzamiento más reciente `SchoolLinux-<tag>.tar.gz`.
3. Descomprima el archivo en la máquina de destino.
4. Ejecute la instalación:

```bash
./install.sh
./run.sh
```

Esta opción es ideal para un despliegue rápido en la máquina del profesor, una vez que el código fuente y la CI han preparado el paquete de lanzamiento.

Tras el inicio, el Frontend del sistema estará disponible en el puerto 8000; las direcciones correspondientes se mostrarán en la terminal.

### 2.2 Instalación manual

### 2.2.1 Requisitos

Servidor (computadora del profesor):

- Linux
- Python 3.12+
- Node.js (se recomienda la LTS actual; en CI se utiliza Node 24) // Solo para instalación manual; la versión de release incluye el Frontend compilado.
- Acceso SSH a los alumnos (puerto 22)

Clientes (computadoras de los alumnos):

- Linux
- Servidor SSH ejecutándose
- Credenciales uniformes para el acceso SSH
- Acceso a la red al servidor del profesor

### 2.2.2 Clonación del repositorio

```bash
git clone https://github.com/A2020GK/SchoolLinux.git
cd SchoolLinux
```

### 2.2.3 Configuración del backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Cree un archivo `.env` en la raíz del proyecto (puede basarse en `.env.example`):

```env
SSH_USER=game
SSH_PASSWORD=game
SSH_TIMEOUT=10
ALLOW_IP_OVERRIDE=false
IP_OVERRIDE_HEADER=X-Debug-IP
```

Explicaciones:

- `SSH_USER`/`SSH_PASSWORD`: credenciales para conectarse a las máquinas de los alumnos.
- `ALLOW_IP_OVERRIDE=true`: utilizar únicamente para depuración local y pruebas.

### 2.2.4 Configuración del frontend

La instalación de dependencias se realiza desde la raíz del proyecto:

```bash
npm install
```

El frontend se encuentra en `frontend/`, la compilación se realiza a través de la configuración de Vite en la raíz.

### 2.2.5 Ejecución en modo dev

Terminal 1 (backend):

```bash
source .venv/bin/activate
fastapi run --host 0.0.0.0
```

Terminal 2 (frontend):

```bash
npx vite --host 0.0.0.0 --port 4000
```

Tras el inicio:

- La API del Backend está disponible en `http://<teacher_ip>:8000`
- El Frontend (Vite dev server) suele estar en `http://<teacher_ip>:4000`

### 2.2.6 Compilación del frontend para producción

```bash
npm run build
```

Los artefactos estarán en `frontend/dist`.
Si el Frontend compilado está presente, el servidor API intentará servir sus archivos en el puerto 8000.

### 2.2.7 Ejecución de pruebas de backend

```bash
source .venv/bin/activate
pytest backend/tests
```

---

## 3. Guía para la creación de juegos personalizados

Los juegos personalizados se añaden sin modificar los módulos internos del backend: basta con crear un nuevo archivo en `backend/app/games/`.

### 3.1 Dónde crear el juego

- Ruta: `backend/app/games/<my_game>.py`
- Los archivos que comienzan con `_` son ignorados por el autodescubrimiento.

Importación recomendada:

```python
from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script
```

### 3.2 Contrato de la clase de juego

Como mínimo, se debe implementar:

```python
class MyGame(Game):
    def install(self, client, game_data):
        ...

    def check(self, client, game_data):
        ...

    def uninstall(self, client, game_data):
        ...
```

Si el juego verifica una respuesta de texto, añada:

```python
string_submission = True

def check_string_submission(self, submission, game_data):
    ...
```

### 3.3 Campos definidos por el autor del juego

- `name`: nombre visible del juego.
- `description`: descripción de la tarea para el alumno.
- `settings_form`: configuraciones editables por el profesor.
- `string_submission`: modo de verificación de respuesta en cadena.
- `anticheat_required`: si se requiere verificación anti-trampas (si se usa en su escenario). // Actualmente no implementado, en proceso.
- `required_user_score`: puntuación objetivo.
- `default_game_data`: plantilla de datos del juego por alumno para la ronda.

Importante:

- En `game_data` guarde solo el progreso del alumno específico durante la ronda.
- Obtenga la configuración del juego desde `self.settings`.
- Elimine siempre los archivos/carpetas creados en `uninstall`.

### 3.4 Tipos de configuración (`GameSettingsItem`)

Tipos soportados:

- `string`
- `number`
- `boolean`
- `option` (requiere un diccionario `options`)

Ejemplo:

```python
settings_form = {
    "difficulty": GameSettingsItem(
        name="Сложность",
        type="option",
        options={"easy": "Easy", "hard": "Hard"},
        default="easy",
    ),
    "files": GameSettingsItem(
        name="Количество файлов",
        type="number",
        default=30,
    ),
}
```

### 3.5 SSH API para autores de juegos

En `backend.app.games`, junto con `Game` y `GameSettingsItem`, se reexportan los ayudantes de SSH:

- `execute_command(client, command)`
    - Ejecuta un comando shell en la máquina del alumno.
    - Devuelve una tupla `(stdout_text, stderr_text)` como cadenas (`str`).
    - Útil en `check` y `uninstall` para comandos cortos.

- `upload_and_run_script(client, name, script)`
    - Sube un script a `/tmp/<name>.sh`, lo hace ejecutable y lo lanza mediante `bash`.
    - Devuelve una tupla `(stdout_text, stderr_text)` como cadenas (`str`).
    - Si el script termina con error (exit code no nulo), lanza un `RuntimeError`.
    - Opción recomendada para `install` cuando se necesitan ejecutar varios comandos seguidos.

Ejemplo de verificación de stderr en `execute_command`:

```python
stdout, stderr = execute_command(client, 'cat "$HOME/Game/message.txt"')
if stderr.strip():
        return 0
content = stdout.strip()
```

### 3.6 Ejemplo mínimo funcional

```python
from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script


class EchoGame(Game):
    name = "Echo"
    description = "Создайте $HOME/Game/message.txt с ожидаемым текстом"
    string_submission = False
    anticheat_required = False
    required_user_score = 1

    settings_form = {
        "expected_text": GameSettingsItem(
            name="Ожидаемый текст",
            type="string",
            default="hello",
        )
    }

    default_game_data = {
        "checked": False,
    }

    def install(self, client, game_data):
        script = """#!/bin/bash
set -e
mkdir -p "$HOME/Game"
"""
        upload_and_run_script(client, "echo_game_install", script)
        game_data["checked"] = False # ¿Se verificó previamente?

    def check(self, client, game_data):
        expected = self.settings["expected_text"]
        stdout, stderr = execute_command(client, 'cat "$HOME/Game/message.txt" 2>/dev/null')
        if stderr.strip():
            return 0
        content = stdout.strip()
        if content == expected and not game_data["checked"]:
            game_data["checked"] = True
            return 1
        return 0

    def uninstall(self, client, game_data):
        execute_command(client, 'rm -rf "$HOME/Game"')

    def check_string_submission(self, submission, game_data):
        return 0
```

### 3.7 Cómo se conecta el juego al sistema

- Al iniciar el backend, se realiza el autodescubrimiento de juegos en `backend/app/games/`.
- La clave del juego corresponde al nombre del archivo (sin `.py`).
- Las configuraciones del juego se guardan automáticamente en el estado global y se restauran al reiniciar.

---

## 4. Diferencias respecto a la v2

A continuación se enumeran los cambios clave respecto a la v2 (rama `v2`).

### 4.1 Arquitectura y base de código

- Antes: estructura de archivos monolítica en la raíz.
- Ahora: estructura modular `backend/app/*` + un `frontend/*` moderno e independiente.

- Antes: énfasis en un único escenario de juego.
- Ahora: modelo de juegos basado en plugins con autodescubrimiento de clases que heredan de `Game`.

### 4.2 Modelo de estado y almacenamiento de datos

- Antes: serialización pickle (`data.pkl`) y formato menos transparente.
- Ahora: JSON (`SLData.json`) con validación, sanitización y un modelo de estado tipado.

- Antes: estados `reg | init | run`.
- Ahora: máquina de estados global explícita `idle | init | running`.

### 4.3 API y modelo de dominio

- Antes: rutas del tipo `/students/*`, `/game/klad`, `/info`.
- Ahora: rutas unificadas `/user/*` y `/game/*` con validación y roles más estrictos.

- Antes: modelo de datos del alumno con `klads` como un conjunto de cadenas bajo la lógica antigua.
- Ahora: `score` + `game_data`, donde el conteo y el progreso son gestionados por el juego específico.

### 4.4 Frontend

- Antes: frontend antiguo.
- Ahora: nuevo frontend en React + TypeScript en `frontend/` con contextos, tipos, capa de API y separación de pantallas Teacher/Student.

- Añadido: modo de previsualización mock mediante variables de entorno (`VITE_MOCK_PREVIEW`, `VITE_MOCK_SCREEN`).

### 4.5 Tiempo real y sincronización

- Antes: actualizaciones básicas en tiempo real.
- Ahora: eventos de Socket.IO formalizados (`users_update`, `kicked`, `game_change`, `game_state_changed`) y una sincronización de UI más predecible.

### 4.6 Testing y CI

- Antes: la documentación se centraba en la ejecución manual.
- Ahora: pruebas integradas de pytest para el backend y flujos de CI:
  - `.github/workflows/tests.yml`: pruebas automáticas del backend.
  - `.github/workflows/frontend-build.yml`: verificación de la compilación del frontend.
  - `.github/workflows/release-tarball.yml`: creación del archivo de lanzamiento basado en etiquetas (tags).

### 4.7 Entrega de Release

- Se ha añadido la creación automática de un archivo tar.gz `SchoolLinux-<tag>.tar.gz` que contiene el backend, el dist del frontend, scripts de ejecución y un `.env` basado en `.env.example`.

---

## Arquitectura y estructura del proyecto

### Backend

- Lenguaje: Python 3.12
- Framework: FastAPI
- Tiempo real: python-socketio (ASGI)
- SSH: Paramiko
- Pruebas: pytest

Directorios principales:

- `backend/app/routers`: rutas HTTP (`/user`, `/game`)
- `backend/app/services`: lógica de negocio
- `backend/app/schemas`: esquemas de pydantic
- `backend/app/socket`: servidor de sockets, gestor de conexiones, manejadores
- `backend/app/games`: juegos integrados y personalizados
- `backend/app/state.py`: carga/guardado del estado de la aplicación

### Frontend

- Lenguaje: TypeScript
- UI: React 19
- Compilación: Vite
- Cliente de tiempo real: socket.io-client

Directorios principales:

- `frontend/views`: pantallas de Teacher/Student
- `frontend/contexts`: contextos de estado globales
- `frontend/api`: clientes HTTP y de sockets tipados
- `frontend/types`: contratos de datos

---

## API y eventos en tiempo real

### HTTP

- `GET /ping`

Usuarios:

- `POST /user/register`
- `GET /user/all` (solo profesor)
- `GET /user/me`
- `DELETE /user/me`
- `POST /user/kick/{ip}` (solo profesor)

Juego:

- `GET /game/`
- `GET /game/list` (solo profesor)
- `POST /game/` (selección de juego/configuración)
- `POST /game/check`
- `POST /game/start`
- `POST /game/stop`
- `GET /game/state`

### Socket.IO

- `users_update`
- `kicked`
- `game_change`
- `game_state_changed`

La ruta del socket está conectada como `/socket.io`.

---

## CI/CD y archivo de lanzamiento

### CI workflows

- `.github/workflows/tests.yml`
  - Ejecuta `pytest backend/tests` en cada push y pull_request.

- `.github/workflows/frontend-build.yml`
  - Verifica la compilación del frontend (`npm run build`) en cada push y pull_request.

- `.github/workflows/release-tarball.yml`
  - Se activa al hacer push de una etiqueta (tag).
  - Compila el frontend, ejecuta las pruebas del backend y genera `SchoolLinux-<tag>.tar.gz`.

### Contenido del release tarball

- `backend/`
- `frontend/dist/`
- `requirements.txt`
- `README.md`
- `install.sh`
- `run.sh`
- `.env` (desde `.env.example`)

Tras descomprimir el archivo:

```bash
./install.sh
./run.sh
```

---

## Limitaciones y recomendaciones prácticas

- El sistema está diseñado principalmente para redes escolares locales.
- El modelo de roles basado en IP (loopback = profesor) es conveniente en el aula, pero no sustituye a una autenticación completa.
- Active `ALLOW_IP_OVERRIDE` solo en depuración/pruebas.
- Antes de la clase, verifique obligatoriamente el acceso SSH a todas las máquinas de los alumnos.
- Para redes inestables, es recomendable realizar un "ensayo" con un juego de prueba corto antes de iniciar la lección.

---

Si desea añadir un nuevo juego, comience por la sección "Guía para la creación de juegos personalizados", cree un archivo en `backend/app/games/` y reinicie el backend: el juego será detectado automáticamente.

---

Developed by Antony Karasev (A2020GK), School №192, Moscow, Russia
