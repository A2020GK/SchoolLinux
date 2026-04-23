# SchoolLinux

Интерактивная учебная платформа для отработки Linux-команд в формате игрового практикума в компьютерном классе.

---

## Содержание

1. [Краткое описание](#1-краткое-описание)
2. [Руководство по установке](#2-руководство-по-установке)
3. [Руководство по созданию кастомных игр](#3-руководство-по-созданию-кастомных-игр)
4. [Отличия от v2](#4-отличия-от-v2)
5. [Архитектура и устройство проекта](#архитектура-и-устройство-проекта)
6. [API и события реального времени](#api-и-события-реального-времени)
7. [CI/CD и релизный архив](#cicd-и-релизный-архив)
8. [Ограничения и практические рекомендации](#ограничения-и-практические-рекомендации)

---

## 1. Краткое описание

SchoolLinux помогает преподавателю проводить практические занятия по Linux терминалу в виде игр.

Как это работает:

- ученики регистрируются через веб-интерфейс.
- Преподаватель выбирает игру и запускает раунд.
- Backend по SSH разворачивает индивидуальные задания на машинах учеников.
- ученики ищут «клады» (или выполняют другие условия игры) в Linux-терминале.
- Прогресс и очки видны преподавателю в реальном времени.

Ключевые особенности текущей версии:

- Плагинная система игр (`backend/app/games/*.py`).
- FastAPI + Socket.IO (ASGI) для REST и realtime-обновлений.
- Типизированное состояние и JSON-персистентность в `SLData.json`.
- React + TypeScript фронтенд с отдельными экранами для преподавателя и ученика.
- Тесты backend (`pytest`) и CI-пайплайны для тестирования и сборки.

---

## 2. Руководство по установке

### 2.1 Release Installation

Если нужен готовый архив без сборки из исходников:

1. Откройте страницу GitHub Releases проекта.
2. Скачайте самый свежий релизный архив `SchoolLinux-<tag>.tar.gz`.
3. Распакуйте архив на целевой машине.
4. Запустите установку:

```bash
./install.sh
./run.sh
```

Этот вариант удобен для быстрого развёртывания на машине преподавателя, когда исходники и CI уже подготовили релизный пакет.

После запуска Frontend системы будет доступен на 8000 порту, соответствующие адреса выводяться в терминал.

### 2.2 Manual installation

### 2.2.1 Требования

Сервер (компьютер преподавателя):

- Linux
- Python 3.12+
- Node.js (рекомендуется актуальная LTS; в CI используется Node 24) // Только при ручной установке, релизная версия содержит собранный Frontend
- Доступ к ученикам по SSH (порт 22)

Клиенты (компьютеры учеников):

- Linux
- Запущенный SSH-сервер
- Единые учетные данные для SSH-доступа
- Доступ к серверу преподавателя по сети

### 2.2.2 Клонирование репозитория

```bash
git clone https://github.com/A2020GK/SchoolLinux.git
cd SchoolLinux
```

### 2.2.3 Настройка backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Создайте `.env` в корне проекта (можно на основе `.env.example`):

```env
SSH_USER=game
SSH_PASSWORD=game
SSH_TIMEOUT=10
ALLOW_IP_OVERRIDE=false
IP_OVERRIDE_HEADER=X-Debug-IP
```

Пояснения:

- `SSH_USER`/`SSH_PASSWORD` - учетные данные для подключения к машинам учеников.
- `ALLOW_IP_OVERRIDE=true` использовать только для локальной отладки и тестов.

### 2.2.4 Настройка frontend

Установка зависимостей выполняется из корня проекта:

```bash
npm install
```

Фронтенд находится в `frontend/`, сборка идет через корневой Vite-конфиг.

### 2.2.5 Запуск в dev-режиме

Терминал 1 (backend):

```bash
source .venv/bin/activate
fastapi run --host 0.0.0.0
```

Терминал 2 (frontend):

```bash
npx vite --host 0.0.0.0 --port 4000
```

После запуска:

- Backend API доступен на `http://<teacher_ip>:8000`
- Frontend (Vite dev server) обычно на `http://<teacher_ip>:4000`

### 2.2.6 Сборка production frontend

```bash
npm run build
```

Артефакты будут в `frontend/dist`.
При наличии собранного Frontend API-сервер будет пытаться отдать его файлы на 8000 порту.

### 2.2.7 Запуск тестов backend

```bash
source .venv/bin/activate
pytest backend/tests
```

---

## 3. Руководство по созданию кастомных игр

Кастомные игры добавляются без изменения внутренних модулей backend: достаточно создать новый файл в `backend/app/games/`.

### 3.1 Где создавать игру

- Путь: `backend/app/games/<my_game>.py`
- Файлы, начинающиеся с `_`, автообнаружением игнорируются.

Рекомендуемый импорт:

```python
from backend.app.games import Game, GameSettingsItem, execute_command, upload_and_run_script
```

### 3.2 Контракт класса игры

Минимум нужно реализовать:

```python
class MyGame(Game):
    def install(self, client, game_data):
        ...

    def check(self, client, game_data):
        ...

    def uninstall(self, client, game_data):
        ...
```

Если игра проверяет текстовый ответ, добавьте:

```python
string_submission = True

def check_string_submission(self, submission, game_data):
    ...
```

### 3.3 Поля, которые определяет автор игры

- `name` - отображаемое название игры.
- `description` - описание задания для ученика.
- `settings_form` - настройки, редактируемые преподавателем.
- `string_submission` - режим проверки строкового ответа.
- `anticheat_required` - требуется ли античит-проверка (если используется в вашем сценарии). // На текущей момент не реализованно, в процессе.
- `required_user_score` - целевой балл
- `default_game_data` - шаблон данных игры на ученика на раунд.

Важно:

- В `game_data` храните только прогресс конкретного ученика во время раунда.
- Конфигурацию игры берите из `self.settings`.
- Всегда удаляйте созданные файлы/папки в `uninstall`.

### 3.4 Типы настроек (`GameSettingsItem`)

Поддерживаемые типы:

- `string`
- `number`
- `boolean`
- `option` (нужен словарь `options`)

Пример:

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

### 3.5 SSH API для авторов игр

В `backend.app.games` вместе с `Game` и `GameSettingsItem` реэкспортируются SSH-хелперы:

- `execute_command(client, command)`
    - Выполняет shell-команду на машине ученика.
    - Возвращает кортеж `(stdout_text, stderr_text)` как строки (`str`).
    - Удобно использовать в `check` и `uninstall` для коротких команд.

- `upload_and_run_script(client, name, script)`
    - Загружает скрипт в `/tmp/<name>.sh`, делает его исполняемым и запускает через `bash`.
    - Возвращает кортеж `(stdout_text, stderr_text)` как строки (`str`).
    - Если скрипт завершился с ошибкой (ненулевой `exit code`), выбрасывает `RuntimeError`.
    - Рекомендуемый вариант для `install`, когда нужно выполнить несколько команд подряд.

Пример проверки stderr у `execute_command`:

```python
stdout, stderr = execute_command(client, 'cat "$HOME/Game/message.txt"')
if stderr.strip():
        return 0
content = stdout.strip()
```

### 3.6 Минимальный рабочий пример

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
        game_data["checked"] = False # Проверяли ли ранее?

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

### 3.7 Как игра подключается в систему

- При старте backend выполняется автообнаружение игр в `backend/app/games/`.
- Ключ игры соответствует имени файла (без `.py`).
- Настройки игры автоматически сохраняются в общем состоянии и восстанавливаются при перезапуске.

---

## 4. Отличия от v2

Ниже перечислены ключевые изменения относительно v2 (ветка `v2`).

### 4.1 Архитектура и кодовая база

- Было: монолитная структура файлов в корне.
- Стало: модульная структура `backend/app/*` + отдельный современный `frontend/*`.

- Было: упор на один сценарий игры.
- Стало: плагинная модель игр с автообнаружением классов-наследников `Game`.

### 4.2 Модель состояния и хранение данных

- Было: pickle-сериализация (`data.pkl`) и менее прозрачный формат.
- Стало: JSON (`SLData.json`) с валидацией, санитизацией и типизированной моделью состояния.

- Было: статус `reg | init | run`.
- Стало: явная глобальная машина состояний `idle | init | running`.

### 4.3 API и доменная модель

- Было: маршруты вида `/students/*`, `/game/klad`, `/info`.
- Стало: унифицированные маршруты `/user/*` и `/game/*` с более строгой валидацией и ролями.

- Было: модель данных ученика с `klads` как набором строк в рамках старой логики.
- Стало: `score` + `game_data`, где подсчет и прогресс управляются конкретной игрой.

### 4.4 Frontend

- Было: старый frontend (сейчас сохранен как `frontend.old/`).
- Стало: новый React + TypeScript frontend в `frontend/` с контекстами, типами, API-слоем и разделением Teacher/Student экранов.

- Добавлено: mock preview режим через переменные окружения (`VITE_MOCK_PREVIEW`, `VITE_MOCK_SCREEN`).

### 4.5 Realtime и синхронизация

- Было: базовые realtime-обновления.
- Стало: формализованные Socket.IO события (`users_update`, `kicked`, `game_change`, `game_state_changed`) и более предсказуемая синхронизация UI.

### 4.6 Тестирование и CI

- Было: документация фокусировалась на ручном запуске.
- Стало: встроенные pytest-тесты backend и CI workflows:
  - `.github/workflows/tests.yml` - автотесты backend.
  - `.github/workflows/frontend-build.yml` - проверка сборки frontend.
  - `.github/workflows/release-tarball.yml` - сборка релизного архива по тегу.

### 4.7 Релизная поставка

- Добавлена автоматическая сборка tar.gz-архива `SchoolLinux-<tag>.tar.gz` с backend, frontend dist, скриптами запуска и `.env` на базе `.env.example`.

---

## Архитектура и устройство проекта

### Backend

- Язык: Python 3.12
- Фреймворк: FastAPI
- Realtime: python-socketio (ASGI)
- SSH: Paramiko
- Тесты: pytest

Основные директории:

- `backend/app/routers` - HTTP-маршруты (`/user`, `/game`)
- `backend/app/services` - бизнес-логика
- `backend/app/schemas` - pydantic-схемы
- `backend/app/socket` - socket-сервер, менеджер подключений, обработчики
- `backend/app/games` - встроенные и кастомные игры
- `backend/app/state.py` - загрузка/сохранение состояния приложения

### Frontend

- Язык: TypeScript
- UI: React 19
- Сборка: Vite
- Realtime-клиент: socket.io-client

Основные директории:

- `frontend/views` - экраны Teacher/Student
- `frontend/contexts` - глобальные контексты состояния
- `frontend/api` - типизированные HTTP и socket-клиенты
- `frontend/types` - контракты данных

---

## API и события реального времени

### HTTP

- `GET /ping`

Пользователи:

- `POST /user/register`
- `GET /user/all` (только преподаватель)
- `GET /user/me`
- `DELETE /user/me`
- `POST /user/kick/{ip}` (только преподаватель)

Игра:

- `GET /game/`
- `GET /game/list` (только преподаватель)
- `POST /game/` (выбор игры/настроек)
- `POST /game/check`
- `POST /game/start`
- `POST /game/stop`
- `GET /game/state`

### Socket.IO

- `users_update`
- `kicked`
- `game_change`
- `game_state_changed`

Сокет-маршрут подключен как `/socket.io`.

---

## CI/CD и релизный архив

### CI workflows

- `.github/workflows/tests.yml`
  - Запускает `pytest backend/tests` на push и pull_request.

- `.github/workflows/frontend-build.yml`
  - Проверяет сборку frontend (`npm run build`) на push и pull_request.

- `.github/workflows/release-tarball.yml`
  - Срабатывает при пуше тега.
  - Строит frontend, гоняет backend-тесты, формирует `SchoolLinux-<tag>.tar.gz`.

### Что внутри release tarball

- `backend/`
- `frontend/dist/`
- `requirements.txt`
- `README.md`
- `install.sh`
- `run.sh`
- `.env` (из `.env.example`)

После распаковки архива:

```bash
./install.sh
./run.sh
```

---

## Ограничения и практические рекомендации

- Система рассчитана прежде всего на локальную школьную сеть.
- Ролевая модель по IP (loopback = преподаватель) удобна в классе, но не заменяет полноценную аутентификацию.
- `ALLOW_IP_OVERRIDE` включайте только в отладке/тестах.
- Перед занятием обязательно проверяйте SSH-доступ до всех машин учеников.
- Для нестабильных сетей полезно провести «прогон» короткой тестовой игры до начала урока.

---

Если вы хотите добавить новую игру, начните с раздела «Руководство по созданию кастомных игр», создайте файл в `backend/app/games/` и перезапустите backend: игра будет обнаружена автоматически.

---

Developed by Antony Karasev (A2020GK), School №192, Moscow, Russia

