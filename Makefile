install:
	yarn global add concurrently
	git submodules init
	git submodules update
	git submodules foreach git checkout origin master
	cd webapp && yarn

start:
	concurrently "docker-compose up" "cd webapp && yarn start"
