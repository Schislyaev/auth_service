#Makefile

up:
	cp env.example/.env.prod.example .env.example
	docker-compose up

build:
	cp env.example/.env.prod.example .env.example
	docker-compose up --build

test:
	cp env.example/.env.test.example .env.example
	docker-compose --file dev.yml up
