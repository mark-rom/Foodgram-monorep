![example workflow](https://github.com/mark-rom/Foodgram-monorep/actions/workflows/foodgram_workflow.yml/badge.svg)

## Foodgram ##
### Description: ###

Foodgram (REST API) is a website where users can publish their recipes, add other recipes to favourites and subscribe to other users. The shopping cart (Список покупок) service allows downloading a list of goods required for selected dishes.

The project is available here: http://foodgram.servehttp.com/
Admins credentials: admin/admin

[Documentation](http://foodgram.servehttp.com//api/docs/) only in Russian, sorry :(

## Technologies ##
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

### Clone repo: ###
    git@github.com:mark-rom/Foodgram-monorep.git

### Go to new dir using command line:: ###
    cd /infra/

### Create .env file and fill it: ###
    touch .env
.env structure is in infra/.env.example

### Launch docker-compose: ###
    docker-compose up -d
____

## Inside the web container ##

#### Migrate: ####
    docker-compose exec web python3 manage.py migrate
  
#### Fill db from .csv file: ####
    docker-compose exec web python3 manage.py populate_ingredient ingredients.csv
  
#### Create superuser: ####
    docker-compose exec web python3 manage.py cratesuperuser

Now service is available on your computer at http://localhost/, admin panel is at http://localhost/admin/
