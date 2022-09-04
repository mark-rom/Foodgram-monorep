![example workflow](https://github.com/mark-rom/yamdb_final/actions/workflows/foodgram_workflow.yml/badge.svg)

## Foodgram ##
### Описание: ###

Foodgram (REST API) - сайт, на котором пользователи могут публиковать собственные рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис "Список покупок" позволяет пользователям создавать список продуктов, которые нужно купить, для приготовления выбранных блюд.

Проект доступен по адресу: http://51.250.110.193/
Доступ администратора стандратный: admin/admin

[Документация](http://51.250.110.193/docs/)

## Технологии ##
- Python 3.10
- Django 4.0.5
- Django REST Framework 3.13.1
- Docker
- Docker-Compose
- PostgreSQL
- Nginx
- Github Workflows
____

## Установка и запуск локально ##

### Клонируйте репозиторий: ###
    git@github.com:mark-rom/foodgram-project-react.git

### Перейдите в репозиторий в командной строке: ###
    cd /infra/

### Создайте .env файл и наполните его: ###
    touch .env
Структура наполнения .env файла представлена в файле .env.example

### Запустите docker-compose в detach-режиме: ###
    docker-compose up -d
____

## Внутри контейнера web ##

#### Выполните миграции: ####
    docker-compose exec web python3 manage.py migrate
  
#### Заполните базу данных из csv файлов: ####
    docker-compose exec web python3 manage.py populate_ingredient ingredients.csv
  
#### Создайте суперюзера: ####
    docker-compose exec web python3 manage.py cratesuperuser

Теперь сервис доступен для работы на вашем компьютере по адресу http://localhost/, а админка – http://localhost/admin/
