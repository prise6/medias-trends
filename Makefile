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


docker-prod-build: package
	docker-compose -f docker-compose-prod.yaml build

docker-prod-up:
	docker-compose -f docker-compose-prod.yaml up -d

docker-prod-stop:
	docker-compose -f docker-compose-prod.yaml stop

docker-prod-exec:
	docker exec -it mediastrends-core-prod /bin/bash


package: .git/HEAD
	python3 setup.py sdist bdist_wheel
	touch package


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


## ----------------------------------------------------------------------------

##
## Makefile as a DAG
##

.DEFAULT_GOAL := get_movies_trends
SHELL:=bash
MD=mediastrends
LOG_FILE=logs/mediastrends_${MEDIASTRENDS_MODE}.txt
.PHONY := get_movie_trends

add_movie_torrents:
	@python scripts/add_movie_torrents.py
	@touch add_movie_torrents

stats_movie_torrents: add_movie_torrents
	@python scripts/stats_movie_torrents.py
	@touch stats_movie_torrents

compute_movie_trends: stats_movie_torrents
	@${MD} -vvvvv torrents trends compute -c movies >> ${LOG_FILE} 2>&1 && \
	${MD} -vvvvv torrents status -c movies >> ${LOG_FILE} 2>&1 && \
	${MD} -vvvvv torrents trends get -c movies >> ${LOG_FILE} 2>&1 && \
	${MD} -vvvvv movies compute >> ${LOG_FILE} 2>&1
	@touch compute_movie_trends
	
get_movie_trends: compute_movie_trends
	@${MD} -vvvvv movies get

clean:
	@rm -f add_movie_torrents
	@rm -f stats_movie_torrents
	@rm -f compute_movie_trends
	@echo "... cleaned"
