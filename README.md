# Foodgram
Cайт Foodgram, «Продуктовый помощник». Пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
- Проект доступен по адресу: <https://vinnipuh.hopto.org/>.
- Администрирование Django: <https://vinnipuh.hopto.org/admin/>
- логин администратора: admin
- пароль для входа в админ-зону: admin
- Документация к API находится по адресу: <https://vinnipuh.hopto.org/api/docs/>.
## Tecnhologies
- Python 3.9.10
- Django 3.2
- Django REST framework 3.14
- Nginx 1.22.1
- Docker
- Postgres 13
## Автор
- Юрий Демидов
## Инструкции по запуску
- Cклонируйте репозиторий себе на локальный компъютер "git clone git@github.com:RV369/foodgram-project-react.git".
- Установитe Windows Subsystem for Linux (WSL2).
- Установите Docker Desktop.
- Создайте файл .env. Шаблон для заполнения файла нахоится в .env.example.
- Выполните команду старта сборки образов "docker-compose up --buld".
- Перейдите в папку backend cd backend.
- Выполните миграции "docker-compose exec backend python manage.py migrate".
- Создайте суперюзера "docker-compose exec backend python manage.py createsuperuser".
- Соберите статику "docker-compose exec backend python manage.py collectstatic ".
- Скопируйте статику "docker compose exec backend cp -r /app/static/. /static/".
- Заполните базу ингредиентами "docker-compose exec backend python manage.py import start".
- Для создания рецепта необходимо создать набор тегов в базе через администрирование: <http://127.0.0.1/admin/login/?next=/admin/>.
- Документация к API находится по адресу: <http://localhost/api/docs/redoc.html>.
## Примеры запросов
- Список рецептов [GET]: <http://localhost/api/recipes/>.
- Создание рецепта [POST]: <http://localhost/api/recipes/>.
- Получение рецепта [GET]: <http://localhost/api/recipes/{id}/>.
- Обновление рецепта [PATCH]: <http://localhost/api/recipes/{id}/>.
- Скачать список покупок [GET]: <http://localhost/api/recipes/download_shopping_cart/>.
- Добавить рецепт в избранное [POST]: <http://localhost/api/recipes/{id}/favorite/>.
- Мои подписки [GET]: <http://localhost/api/users/subscriptions/>.
- Список ингредиентов [GET]: <http://localhost/api/ingredients/>.
