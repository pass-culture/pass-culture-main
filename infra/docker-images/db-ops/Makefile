unit-tests:
	docker-compose run db-ops bash -c "cd /scripts && python -m unittest discover -s tests/unit"

e2e-tests:
	docker-compose run db-ops pytest -s /scripts/tests/e2e/test_workflow.py