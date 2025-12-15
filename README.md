# FitPlans Platform

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Django](https://img.shields.io/badge/django-5.0-green.svg)
![Django Ninja](https://img.shields.io/badge/django--ninja-1.3-red.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)

**FitPlans** — это современная платформа для продажи и управления тренировочными планами. Проект разработан с использованием **Django** и **Django Ninja** для создания высокопроизводительного асинхронного API.

## 🚀 Технологический стек

*   **Backend:** Python 3.12, Django 5.0, Django Ninja (FastAPI-like syntax)
*   **Database:** PostgreSQL 15
*   **Cache & Broker:** Redis 7
*   **Async Tasks:** Celery
*   **Validation:** Pydantic V2
*   **Auth:** JWT (Access + Refresh)
*   **Deployment:** Docker & Docker Compose

## 🛠 Функциональность

*   **Пользователи:**
    *   Регистрация и аутентификация (JWT).
    *   Управление профилем (рост, вес, цели).
    *   Загрузка аватарок с автоматическим ресайзом и валидацией.
    *   Трекинг прогресса (вес, заметки) с историей.
*   **Тренировки (В разработке):**
    *   Создание планов тренировок тренерами.
    *   Покупка и подписка на планы.
    *   Просмотр упражнений и видео-инструкций.

## 📦 Запуск проекта

Проект полностью контейнеризирован. Для запуска вам понадобятся **Docker** и **Docker Compose**.

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/KXNY4/FitPlans.git
    cd FitPlans
    ```

2.  **Создайте файл окружения:**
    Создайте файл `.env.docker` на основе примера (или используйте дефолтные настройки для разработки).

3.  **Запустите контейнеры:**
    ```bash
    docker-compose up --build
    ```

    При первом запуске автоматически:
    *   Применятся миграции базы данных.
    *   Соберется статика.
    *   Создастся суперпользователь (если указан в `.env`).

4.  **Доступ к API:**
    *   Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
    *   Admin Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)

## 🧪 Разработка

Для локальной разработки без Docker используется **Poetry**:

```bash
poetry install
poetry shell
python manage.py migrate
python manage.py runserver
```

## 📝 Лицензия

This project is licensed under the MIT License.
