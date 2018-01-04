dev:
	concurrently "make watch-build" "make watch-serve"

watch-build:
	concurrently "make watch-concat" "nodemon --watch apiary.apib.md -e md --exec \"sh scripts/build.sh\""

watch-concat:
	nodemon --watch src -e md --exec "sh scripts/concat.sh"

watch-serve:
	concurrently "nodemon --watch apiary.htm -e htm --exec \"sh scripts/serve_mock.sh\"" "sh scripts/serve_htm.sh"
