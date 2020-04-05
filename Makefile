


##
## DEV COMMANDS - FROM OUTSIDE CONTAINER
##

docker-dev-build:
	cp requirements.txt docker/
	docker-compose -f docker-compose-dev.yaml build

docker-dev-up:
	docker-compose -f docker-compose-dev.yaml up -d

docker-dev-stop:
	docker-compose -f docker-compose-dev.yaml stop

docker-dev-exec:
	docker exec -it mediastrends-core-dev /bin/bash


##
## DEV COMMANDS - INSIDE CORE CONTAINER
## 

install-dev:
	pip install -e .

unittest:
	python -m unittest discover -s tests

flake8:
	flake8 mediastrends --count --statistics --ignore=E501,W503 --show-source

##
## PROD COMMANDS - INSIDE CORE CONTAINER
## 

install-prod:
	pip install .