.PHONY: build run rebuild

build:
	docker-compose up -d build --scale chainlit=3

run:
	docker-compose up -d --scale chainlit=3

rebuild:
	docker compose down -v --remove-orphans && docker compose up -d --build --scale chainlit=3