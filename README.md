# Cайт Recipes Assistant «Помощник для работы с рецептами»

### Описание
На сервисе Foodgram пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. 
В ходе реализации проекта мною были реализованы:
1. бэкенд проекта на Django REST Framework (реализовано API по готовой спецификации)
2. созданы Dockerfile для контейнера бэкенда
3. создана конфигурация сервера nginx
4. созданы конфигурации для запуска docker контейнеров для базы данных (PostgreSQL),
для HTTP-сервера nginx, для фронтенда и бэкенда (файл docker-compose)


### О проекте
Проект базируется на следующих технологиях:
1. Python 3.8
2. Django 3.2.11
3. Django REST Framework 3.13.1
4. PostgreSQL 
5. django-filter 21.1
6. Pillow 9.0 (для загрузки изображений)
7. reportlab 3.6.8 (для формирования документа в формате PDF)
8. Poetry  (для разработки проекта в отдельном окружении и работы с зависимостями проекта)
9. Git (GitHub) (для сохранения и отслеживания изменений кода)
10. Линтер Flake8 (для проверки соответствия кода стандарту PEP8)
11. Docker (для запуска проекта в контейнерах)
12. Gunicorn
13. Nginx


### Установка и запуск проекта:

1. Установите Docker и Docker-compose
```
 sudo apt install docker.io
 sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
 sudo chmod +x /usr/local/bin/docker-compose
```

2. Скопируйте файлы Docker-compose.yml и nginx.conf из папки infra репозитория
https://github.com/SvetlanaLogvinova88/foodgram-project-react.git
Также необходимо скопировать файл ingredients.csv из папки data указанного репозитория.

3. Создайте файл .env в папке со скопированными из репозитория файлами со следующим
содержимым:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

4. Перейдите с папку со скопированными из репозитория файлами и запустите проект:
```
sudo docker-compose up -d --build
```

5. Соберите статику и проведите миграции:
<CONTAINER ID> - id контейнера backend
```
docker-compose exec <CONTAINER ID> python3 manage.py collectstatic --noinput
docker exec -it <CONTAINER ID> bash
python manage.py makemigrations
python manage.py migrate --noinput
```

6. Создайте суперпользователя для сайта:
```
docker exec -it <CONTAINER ID> bash
python manage.py createsuperuser
```

7. загрузите список ингредиентов на сайт:
```
docker cp ingredients.csv <CONTAINER ID>:/code
docker exec -it <CONTAINER ID> bash
python manage.py load_ingridients /code/ingredients.csv
```

8. зайдите в админку сайта и создайте теги рецептов.


### Примеры запросов:

POST http://localhost:8000/api/users/ - регистрация
POST http://localhost:8000/api/auth/token/login - создание токена
GET http://localhost:8000/api/users/ - Просмотр информации о пользователях

POST http://localhost:8000/api/users/set_password/ - Изменение пароля
GET http://localhost:8000/api/users/4/subscribe/ - Подписаться на пользователя
DEL http://localhost:8000/api/users/4/subscribe/ - Отписаться от пользователя

POST http://localhost:8000/api/recipes/ - Создать рецепт
GET http://localhost:8000/api/recipes/ - Получить рецепты
GET http://localhost:8000/api/recipes/<id>/ - Получить рецепт по id
DEL http://localhost:8000/api/recipes/<id>/ - Удалить рецепт по id

GET http://localhost:8000/api/recipes/<id>/favorite/ - Добавить рецепт в избранное
DEL http://localhost:8000/api/recipes/<id>/favorite/ - Удалить рецепт из избранного

GET http://localhost:8000/api/users/<id>/subscribe/ - Подписаться на пользователя
DEL http://localhost:8000/api/users/<id>/subscribe/ - Отписаться от пользователя

GET http://localhost:8000/api/ingredients/ - Получить список всех ингредиентов

GET http://localhost:8000/api/tags/ - Получить список всех тегов

GET http://localhost:8000/api/recipes/<id>/shopping_cart/ - Добавить рецепт в корзину
DEL http://localhost:8000/api/recipes/<id>/shopping_cart/ - Удалить рецепт из корзины
