import cloudsqlpostgresinstance
import env_vars

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.SOURCE_PROJECT,
    name=env_vars.SOURCE_INSTANCE,
    region=env_vars.SOURCE_INSTANCE_REGION,
)

ehp.backup()
