.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up

.PHONY: stop
stop:
	docker-compose stop