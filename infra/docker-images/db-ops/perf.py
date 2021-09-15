import cloudsqlpostgresinstance
import env_vars
from passculture_db_ops import transform_database

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    name=env_vars.SOURCE_INSTANCE,
    project="passculture-metier-ehp",
    region=env_vars.SOURCE_INSTANCE_REGION,
)

perf = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    name=env_vars.DEST_INSTANCE,
    project="passculture-metier-ehp",
    region=env_vars.DEST_INSTANCE_REGION,
)

# 1 Restore backup
perf.restore_backup(
    backup_id=ehp.get_last_successful_backup_run_id(),
    backup_instance_id=ehp.name,
    backup_instance_project=ehp.project
)

# 2 Update source user password
perf.update_user_password(username=env_vars.SOURCE_USER, password=env_vars.SOURCE_USER_TEMP_PASSWORD)

# 3 Create new user
perf.create_user(username=env_vars.DEST_NEW_USER, password=env_vars.DEST_NEW_USER_PASSWORD)

# 4 Rename database and change owner
transform_database(
    instance=perf,
    old_database_name=env_vars.SOURCE_DATABASE_NAME,
    new_database_name=env_vars.DEST_DATABASE_NAME,
    owner=env_vars.SOURCE_USER,
    owner_password=env_vars.SOURCE_USER_TEMP_PASSWORD,
    new_owner=env_vars.DEST_NEW_USER,
    new_owner_password=env_vars.DEST_NEW_USER_PASSWORD,
)