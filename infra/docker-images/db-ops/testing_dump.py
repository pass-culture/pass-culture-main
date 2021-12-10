import cloudsqlpostgresinstance
from os import getenv

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=getenv("TESTING_INSTANCE_PROJECT", "passculture-metier-ehp"),
    name=getenv("TESTING_INSTANCE_NAME"),
    region=getenv("TESTING_INSTANCE_REGION", "europe-west1"),
)

ehp.export_dump(database_name="pcapi-testing", dump_uri="gs://%s/pcapi-testing.gz" % getenv("DUMP_BUCKET"))
