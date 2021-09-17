import cloudsqlpostgresinstance
import env_vars

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.SOURCE_PROJECT,
    name=env_vars.SOURCE_INSTANCE,
    region=env_vars.SOURCE_INSTANCE_REGION,
)

databases_to_export = env_vars.SOURCE_DATABASES_TO_EXPORT.split(",")

for database in databases_to_export:
    ehp.export_dump(database_name=database, dump_uri="gs://%s/%s.gz" % (env_vars.DUMP_BUCKET, database))
