# Foodgram ![CI](https://github.com/M4rk-er/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)


### сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Использованные технологии/пакеты
* Python 3.7
* Django 3.1.4
* django-filter 21.1
* djangorestframework 3.14.0
* djoser 2.0.1
* gunicorn 20.0.4
* nginx
* postgreSQL

#### Если Docker не установлен, перейдите на [официальный сайт ](https://www.docker.com/products/docker-desktop) и скачайте установочный файл Docker Desktop для вашей операционной системы

### Клонировать репрозиторий:
```
git@github.com:M4rk-er/foodgram-project-react.git
``` 

### После клонирования репрозитория:

- Перейдите в директорию infra
``` 
cd infra 
```
- Создать файл ``` .env ```

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432 
```
- Собрать и запустить контейнеры:
``` 
docker-compose up -d --build 
```

- Выполнить миграции:
``` 
docker-compose exec backend python manage.py migrate 
```

- Создать суперпользователя:
``` 
docker-compose exec backend python3 manage.py createsuperuser 
```

- Собрать staticfiles:
``` 
docker-compose exec backend python3 manage.py collectstatic --noinput 
```

### После запуска проект будет доступен по адресу localhost, [панель администратора](localhost/admin/)

# http://158.160.37.167/

## email: admin@admin.ru
## password: admin
