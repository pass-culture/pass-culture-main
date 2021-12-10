from datetime import datetime

import cloudsqlpostgresinstance
from os import getenv

testing = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=getenv("TESTING_INSTANCE_PROJECT", "passculture-metier-ehp"),
    name=getenv("TESTING_INSTANCE_NAME"),
    region=getenv("TESTING_INSTANCE_REGION", "europe-west1"),
)

testing_user = getenv("TESTING_USER", "pcapi-testing")

testing.create_user(testing_user, getenv("TESTING_USER_PASSWORD"))

testing_database_name = getenv("TESTING_DATABASE_NAME", "pcapi-testing")
testing.create_database(testing_database_name)

dump_bucket = getenv("DUMP_BUCKET")

try:
    dump_uri = "gs://%s/%s.gz" % (dump_bucket, testing_database_name)
    print("Restoring dump %s to %s" % (dump_uri, testing.name))
    testing.import_dump(
        target_database=testing_database_name,
        dump_uri="gs://%s/%s.gz" % (dump_bucket, testing_database_name),
        import_user=testing_user
    )
    print("Ended: Restoring dump %s to %s @%s" % (dump_uri, testing.name, datetime.now()))
except Exception as e:
    print("Import failed, dropping newly created database %s" % testing_database_name)
    testing.drop_database(testing_database_name)
    print("Import failed, dropping newly created role %s" % testing_user)
    testing.drop_role(testing_user)
