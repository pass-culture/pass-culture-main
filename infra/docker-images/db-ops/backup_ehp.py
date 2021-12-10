import cloudsqlpostgresinstance
from os import getenv

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=getenv("EHP_INSTANCE_PROJECT", "passculture-metier-ehp"),
    name=getenv("EHP_INSTANCE_NAME"),
    region=getenv("EHP_INSTANCE_REGION", "europe-west1"),
)

ehp.backup()
