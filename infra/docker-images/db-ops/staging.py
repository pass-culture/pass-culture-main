import cloudsqlpostgresinstance
import passculture_db_ops
import env_vars
import os

prod = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.SOURCE_PROJECT,
    name=env_vars.SOURCE_INSTANCE,
    region=env_vars.SOURCE_INSTANCE_REGION,
)

ehp = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=env_vars.DEST_PROJECT,
    name=env_vars.DEST_INSTANCE,
    region=env_vars.DEST_INSTANCE_REGION,
)

# 1 Delete replicas
replica_names = ehp.get_replica_names()
for replica_name in replica_names:
    ehp.delete_replica(replica_name)

# 2 Restore backup
backup_id = prod.get_last_successful_backup_run_id()
ehp.restore_backup(backup_id=backup_id, backup_instance_id=prod.name, backup_instance_project=prod.project)

# 3 Recreate replicas
for replica_name in replica_names:
    ehp.create_replica(replica_name)

# 4 Update source user password
ehp.update_user_password(username=env_vars.SOURCE_USER, password=env_vars.SOURCE_USER_TEMP_PASSWORD)

# 5 Create new user
ehp.create_user(username=env_vars.DEST_NEW_USER, password=env_vars.DEST_NEW_USER_PASSWORD)

# 6 Rename database and change owner
passculture_db_ops.transform_database(
    instance=ehp,
    old_database_name=env_vars.SOURCE_DATABASE_NAME,
    new_database_name=env_vars.DEST_DATABASE_NAME,
    owner=env_vars.SOURCE_USER,
    owner_password=env_vars.SOURCE_USER_TEMP_PASSWORD,
    new_owner=env_vars.DEST_NEW_USER,
    new_owner_password=env_vars.DEST_NEW_USER_PASSWORD,
)

if not env_vars.DEST_DATABASE_HOST:
    env_vars.DEST_DATABASE_HOST = ehp.get_ip_address(ip_address_type=env_vars.DEST_INSTANCE_IP_ADDRESS_TYPE)

ehp.connect(
    username=env_vars.DEST_NEW_USER,
    password=env_vars.DEST_NEW_USER_PASSWORD,
    database=env_vars.DEST_DATABASE_NAME
)

database_url = passculture_db_ops.build_database_url(
    username=env_vars.DEST_NEW_USER,
    password=env_vars.DEST_NEW_USER_PASSWORD,
    database_name=env_vars.DEST_DATABASE_NAME,
    database_host=env_vars.DEST_DATABASE_HOST,
    database_port=env_vars.DEST_DATABASE_PORT,
)

# 7 Post-process
os.environ["DATABASE_URL"] = database_url

passculture_db_ops.post_process(
    instance=ehp,
    database_url=database_url
)

passculture_db_ops.run_flask_command("sandbox", "--name", "beneficiaries", "--clean", "false")

ehp.disconnect()

# 8 Backup
ehp.backup()
