# Makefile

.PHONY: build up up-d logs down shell

# Сборка образа бота
build:
	docker compose build

# Запуск в интерактивном режиме (для отладки)
up: build
	docker compose up

# Запуск в фоновом режиме
up-d: build
	docker compose up -d

# Просмотр логов
logs:
	docker compose logs -f

# Остановка и удаление контейнеров
down:
	docker compose down -v
	
# Запуск bash внутри контейнера бота
shell:
	docker compose exec bot bash