.PHONY: build run rebuild

build_scale:
	docker-compose up -d --build --scale chainlit=3

run_scale:
	docker-compose up -d --scale chainlit=3

rebuild_scale:
	docker compose down -v --remove-orphans && docker compose up -d --build --scale chainlit=3

down:
	docker compose down -v --remove-orphans

simple_up:
	docker compose up -d

simple_build:
	docker compose up -d --build