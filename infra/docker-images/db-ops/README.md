### Docker Image for Database Operations

This image is used in the passculture-db-operations helm chart.

This image contains:
- the postgresql client (used to run the anonymisation script)
- the pcapi app (used to run the user import script)

# Tests

To run the tests, use the Makefile targets. You'll need to mount your Google Cloud credentials in order to run the end
end to end tests.