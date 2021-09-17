from datetime import datetime

import cloudsqlpostgresinstance
import env_vars

testing = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.DEST_PROJECT,
    name=env_vars.DEST_INSTANCE,
    region=env_vars.DEST_INSTANCE_REGION,
)

testing.create_user(env_vars.DEST_NEW_USER, env_vars.DEST_NEW_USER_PASSWORD)
testing.create_database(env_vars.DEST_DATABASE_NAME)

try:
    dump_uri = "gs://%s/%s.gz" % (env_vars.DUMP_BUCKET, env_vars.DEST_DATABASE_NAME)
    print("Restoring dump %s to %s" % (dump_uri, testing.name))
    testing.import_dump(
        target_database=env_vars.DEST_DATABASE_NAME,
        dump_uri="gs://%s/%s.gz" % (env_vars.DUMP_BUCKET, env_vars.DEST_DATABASE_NAME),
        import_user=env_vars.DEST_NEW_USER
    )
    print("Ended: Restoring dump %s to %s @%s" % (dump_uri, testing.name, datetime.now()))
except Exception as e:
    print("Import failed, dropping newly created database %s" % env_vars.DEST_DATABASE_NAME)
    testing.drop_database(env_vars.DEST_DATABASE_NAME)
    print("Import failed, dropping newly created role %s" % env_vars.DEST_NEW_USER)
    testing.drop_role(env_vars.DEST_NEW_USER)
