ssh:
	ssh deploy@pc-api.btmx.fr

install:
	yarn global add concurrently
	git submodules init
	git submodules update
	git submodules foreach git checkout origin master
	cd webapp && yarn

recreate:
	rm -rf api/postgres_data
	docker-compose up --force-recreate

start:
	concurrently "docker-compose up" "cd webapp && yarn start"
