rebuild:
	docker-compose build --no-cache
	rm -rf api/postgres_data

dump_db:
	mkdir -p $(dir $(realpath $(firstword $(MAKEFILE_LIST))))db_dumps
	docker exec `docker ps | grep postgres | cut -d' ' -f 1` pg_dump -d pass_culture -U pass_culture -F c > $(dir $(realpath $(firstword $(MAKEFILE_LIST))))db_dumps/`date +%Y%m%d_%H%M%S`.pgdump

init-dev:
	cd api && make init-dev

init-prod:
	cd api && make init-prod

install:
	yarn global add concurrently
	git submodules init
	git submodules update
	git submodules foreach git checkout origin master
	cd webapp && yarn

recreate:
	rm -rf api/static/object_store_data
	rm -rf api/postgres_data
	docker-compose up

restore_db:
	cat $(backup_file) | docker exec -i `docker ps | grep postgres | cut -d' ' -f 1` pg_restore -d pass_culture -U pass_culture -c

ssh:
	ssh deploy@pc-api.btmx.fr

start:
	concurrently "docker-compose up" "cd webapp && yarn start"

update:
	cd $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
	git fetch && git reset --hard && git checkout origin/master && git reset --hard
	cd dockerfiles/nginx/conf.d && rm flaskapp.conf && ln -s flaskapp_ssl flaskapp.conf && cd
	git submodule foreach bash -c "git fetch && git reset --hard && git checkout origin/master && git reset --hard"
