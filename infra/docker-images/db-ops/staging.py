import cloudsqlpostgresinstance
import passculture_db_ops
from os import getenv, environ

production_instance_name = environ["PRODUCTION_INSTANCE_NAME"]
production_user = getenv("PRODUCTION_USER", "pcapi-production")
production_user_temp_password = getenv("PRODUCTION_USER_TEMP_PASSWORD", passculture_db_ops.generate_random_string(13))

staging_instance_name = environ["STAGING_INSTANCE_NAME"]
staging_user = getenv("STAGING_USER", "pcapi-staging")
staging_user_password = environ["STAGING_USER_PASSWORD"]

production_instance = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=getenv("PRODUCTION_INSTANCE_PROJECT", "passculture-metier-prod"),
    name=production_instance_name,
    region=getenv("PRODUCTION_INSTANCE_REGION", "europe-west1"),
)

staging_instance = cloudsqlpostgresinstance.CloudSQLPostgresInstanceFactory.create(
    project=getenv("STAGING_INSTANCE_PROJECT", "passculture-metier-ehp"),
    name=staging_instance_name,
    region=getenv("STAGING_INSTANCE_REGION", "europe-west1")
)

# 1 Delete replicas
replica_names = staging_instance.get_replica_names()
for replica_name in replica_names:
    staging_instance.delete_replica(replica_name)

# 2 Restore backup
backup_id = production_instance.get_last_successful_backup_run_id()
staging_instance.restore_backup(backup_id=backup_id, backup_instance_id=production_instance.name, backup_instance_project=production_instance.project)

# 3 Recreate replicas
for replica_name in replica_names:
    staging_instance.create_replica(replica_name)

# 4 Update source user password on ehp
staging_instance.update_user_password(username=production_user, password=production_user_temp_password)

# 5 Create new user
staging_instance.create_user(username=staging_user, password=staging_user_password)

staging_database_name = getenv("STAGING_DATABASE_NAME", "pcapi-staging")

# 6 Rename database and change owner
passculture_db_ops.rename_database_and_change_owner(
    instance=staging_instance,
    old_database_name=getenv("PRODUCTION_DATABASE_NAME", "pcapi-production"),
    new_database_name=staging_database_name,
    owner=production_user,
    owner_password=production_user_temp_password,
    new_owner=staging_user,
    new_owner_password=staging_user_password,
)

staging_instance_host = getenv("STAGING_INSTANCE_HOST", staging_instance.get_ip_address(ip_address_type=getenv("STAGING_INSTANCE_IP_ADDRESS_TYPE", "public")))

staging_instance.connect(
    username=staging_user,
    password=staging_user_password,
    database=staging_database_name
)

database_url = passculture_db_ops.build_database_url(
    username=staging_user,
    password=staging_user_password,
    database_name=staging_database_name,
    database_host=staging_instance_host,
    database_port=getenv("STAGING_INSTANCE_PORT", 5432),
)

# 7 Post-process
environ["DATABASE_URL"] = database_url

passculture_db_ops.empty_tables(
    instance=staging_instance,
    tables=list( filter(None, getenv("STAGING_TABLES_TO_EMPTY", "activity user_session email").split(" ") ) )
)
passculture_db_ops.anonymize(database_url=database_url)
passculture_db_ops.import_users()
passculture_db_ops.disable_venue_providers(staging_instance)

passculture_db_ops.run_flask_command("sandbox", "--name", "beneficiaries", "--clean", "false")

passculture_db_ops.run_flask_command(
    "process_offers_from_database",
    "--clear=%s" % getenv("REINDEX_OFFERS_CLEAR_OFFERS", "true").lower(),
    "--starting-page=%s" % getenv("REINDEX_OFFERS_STARTING_PAGE", "0"),
    "--ending-page=%s"  % getenv("REINDEX_OFFERS_ENDING_PAGE", "1"),
    "--limit=%s" % getenv("REINDEX_OFFERS_LIMIT", "10000")
)

staging_instance.disconnect()

# 8 Backup
staging_instance.backup()
