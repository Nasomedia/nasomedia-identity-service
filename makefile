.PHONY: build, run, down, restart

build:
	sudo docker-comopse build
up:
	sudo docker-compose up -d --build

down:
	sudo docker-compose down --volumes

restart:
	sudo docker-compose restart