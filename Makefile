.PHONY: build_scale down run build

build_scale:
	docker-compose up -d --build --scale chainlit=3

down:
	docker compose down -v --remove-orphans

run:
	docker compose up -d

build:
	docker compose up -d --build