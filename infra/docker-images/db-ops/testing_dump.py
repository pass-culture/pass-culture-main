import cloudsqlpostgresinstance
import env_vars

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.SOURCE_PROJECT,
    name=env_vars.SOURCE_INSTANCE,
    region=env_vars.SOURCE_INSTANCE_REGION,
)

ehp.export_dump(database_name="pcapi-testing", dump_uri="gs://%s/testing.gz" % env_vars.DUMP_BUCKET)
