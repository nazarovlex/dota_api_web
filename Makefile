
.PHONY: install_requirements
install_requirements:
	pip install -r requirements.txt

.PHONY: build
build:
	docker-compose build

.PHONY: start
start:
	docker-compose up --no-attach mongo

.PHONY: stop
stop:
	docker-compose stop

.PHONY: clean
clean:
	sudo rm -rf .artifacts

.PHONY: restart
restart:
	make clean
	make build
	make start

.PHONY: prune
prune:
	docker system prune




