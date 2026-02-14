.PHONY: help build up down restart logs shell dbshell migrate makemigrations createsuperuser collectstatic loaddata clean

help:
	@echo "Django Library - Docker Commands"
	@echo "================================="
	@echo "make build          - Побудувати Docker образи"
	@echo "make up             - Запустити контейнери"
	@echo "make down           - Зупинити контейнери"
	@echo "make restart        - Перезапустити контейнери"
	@echo "make logs           - Показати логи"
	@echo "make shell          - Django shell"
	@echo "make dbshell        - PostgreSQL shell"
	@echo "make migrate        - Застосувати міграції"
	@echo "make makemigrations - Створити міграції"
	@echo "make createsuperuser- Створити суперкористувача"
	@echo "make collectstatic  - Зібрати статичні файли"
	@echo "make loaddata       - Завантажити тестові дані"
	@echo "make clean          - Очистити контейнери та volumes"

build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-db:
	docker-compose logs -f db

shell:
	docker-compose exec web python manage.py shell

dbshell:
	docker-compose exec web python manage.py dbshell

psql:
	docker-compose exec db psql -U library_user -d library_db

migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

loaddata:
	docker-compose exec web python manage.py loaddata library/fixtures/initial_data.json

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f

backup:
	docker exec library_postgres pg_dump -U library_user library_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"

ps:
	docker-compose ps

stats:
	docker stats library_django library_postgres
