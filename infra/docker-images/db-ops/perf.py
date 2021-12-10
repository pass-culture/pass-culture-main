import cloudsqlpostgresinstance
from os import getenv, environ
from passculture_db_ops import rename_database_and_change_owner, generate_random_string

staging_instance_name = environ["STAGING_INSTANCE_NAME"]
staging_user = getenv("STAGING_USER", "pcapi-staging")
staging_user_temp_password = getenv("STAGING_USER_TEMP_PASSWORD", generate_random_string(13))

perf_instance_name = environ["PERF_INSTANCE_NAME"]
perf_user = getenv("PERF_USER", "pcapi-perf")
perf_user_password = environ["PERF_USER_PASSWORD"]

staging_instance = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    name=staging_instance_name,
    project=getenv("STAGING_INSTANCE_PROJECT", "passculture-metier-ehp"),
    region=getenv("STAGING_INSTANCE_REGION", "europe-west1"),
)

perf_instance = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    name=perf_instance_name,
    project=getenv("PERF_INSTANCE_PROJECT", "passculture-metier-ehp"),
    region=getenv("PERF_INSTANCE_REGION", "europe-west1"),
)

# 1 Restore backup
perf_instance.restore_backup(
    backup_id=staging_instance.get_last_successful_backup_run_id(),
    backup_instance_id=staging_instance.name,
    backup_instance_project=staging_instance.project
)

# 2 Update source user password
perf_instance.update_user_password(username=staging_user, password=staging_user_temp_password)

# 3 Create new user
perf_instance.create_user(username=perf_user, password=perf_user_password)

# 4 Rename database and change owner
rename_database_and_change_owner(
    instance=perf_instance,
    old_database_name=getenv("PERF_DATABASE_NAME", "pcapi-perf"),
    new_database_name=getenv("STAGING_DATABASE_NAME", "pcapi-staging"),
    owner=staging_user,
    owner_password=staging_user_temp_password,
    new_owner=perf_user,
    new_owner_password=perf_user_password,
)