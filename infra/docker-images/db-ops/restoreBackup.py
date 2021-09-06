from os import getenv, environ
from time import sleep
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from datetime import datetime
from google.cloud.sql.connector import connector
import subprocess
import random
import string

SOURCE_PROJECT = getenv("SOURCE_PROJECT")
SOURCE_INSTANCE = getenv("SOURCE_INSTANCE")
DEST_PROJECT = getenv("DEST_PROJECT")
DEST_INSTANCE = getenv("DEST_INSTANCE")
DEST_INSTANCE_IP_ADDRESS_TYPE = getenv("DEST_INSTANCE_IP_ADDRESS_TYPE", "PRIVATE").upper()
DEST_DATABASE_HOST = getenv("DEST_DATABASE_HOST")

SOURCE_USER = getenv("SOURCE_USER")
SOURCE_USER_TEMP_PASSWORD = getenv("SOURCE_USER_TEMP_PASSWORD",
                                   ''.join(random.choice(string.ascii_letters + string.digits) for i in range(13)))
SOURCE_DATABASE_NAME = getenv("SOURCE_DATABASE_NAME", SOURCE_USER)

DEST_NEW_USER = getenv("DEST_NEW_USER")
DEST_NEW_USER_PASSWORD = getenv("DEST_NEW_USER_PASSWORD")
DEST_DATABASE_NAME = getenv("DEST_DATABASE_NAME", DEST_NEW_USER)

DEST_DATABASE_PORT = getenv("DEST_DATABASE_PORT", 5432)

ANONYMIZE_SQL_SCRIPT_PATH = getenv("ANONYMIZE_SQL_SCRIPT_PATH")
PCAPI_ROOT_PATH = getenv("PCAPI_ROOT_PATH")
IMPORT_USERS_SCRIPT_PATH = getenv("IMPORT_USERS_SCRIPT_PATH")
USERS_CSV_PATH = getenv("USERS_CSV_PATH")

POST_PROCESS = getenv("POST_PROCESS") == "TRUE"
TABLES_TO_EMPTY = getenv("TABLES_TO_EMPTY", "").split(" ") if getenv("TABLES_TO_EMPTY") != "" else []

'''
Client library for Google's discovery based APIs constant
https://github.com/googleapis/google-api-python-client/blob/main/googleapiclient/discovery.py

Here we build the client for sqladmin API with the v1beta4 version
'''
SQLADMIN = discovery.build('sqladmin', 'v1beta4')

'''
Cloud SQL Admin API backupRuns constant
backupRuns()
https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.backupRuns.html
'''
SQLADMIN_BACKUP_RUNS = SQLADMIN.backupRuns()

'''
Cloud SQL Admin API instances constant
instances()
https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.instances.html
'''
SQLADMIN_INSTANCES = SQLADMIN.instances()


def get_instance_info(project: str, instance: str):
    return SQLADMIN_INSTANCES.get(project=project, instance=instance).execute()


def get_backup_runs_list(project: str, instance: str):
    """
    This function returns a dictionary of backup runs from an instance of a project
    It calls the list() function from the Cloud SQL Admin API
    https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/sqladmin_v1beta4.backupRuns.html#list
    """
    backup_runs_list = None
    try:
        backup_runs_list = SQLADMIN_BACKUP_RUNS.list(
            project=project, instance=instance).execute()
    except(HttpError) as http_error:
        print("An error occured while querying the Cloud SQL Admin API", http_error)

    return backup_runs_list


def get_last_successful_backup_run_id(project: str, instance: str) -> str:
    """
    This function returns the backupRunId (that has a successful status)
    If there are no successful backupRun the function throws an exception
    """
    last_successful_backup_run_id = None
    backup_runs_list = get_backup_runs_list(
        project=project, instance=instance)['items']
    try:
        for item in backup_runs_list:
            if item['status'] == "SUCCESSFUL":
                last_successful_backup_run_id = item
                print("Last successful backup id %s from %s" %
                      (last_successful_backup_run_id["id"],
                       datetime.strptime(last_successful_backup_run_id["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ")))
                return last_successful_backup_run_id["id"]
        else:
            raise Exception("Can't find a successful backup")
    except BaseException as error:
        print('An exception occurred : {}'.format(error))


def connect_to_dest_instance(user: str, password: str, database: str, use_iam_auth: bool = False):
    connection = connector.connect(
        "%s:europe-west1:%s" % (DEST_PROJECT, DEST_INSTANCE),
        "pg8000",
        user=user,
        password=password,
        db=database,
        enable_iam_auth=use_iam_auth,
    )
    # Execute a query
    connection.autocommit = True
    return connection


def get_instance_ip_address(project: str, instance: str, ip_address_type: str):
    if ip_address_type == "PUBLIC":
        ip_address_type = "PRIMARY"
    for item in get_instance_info(project, instance)["ipAddresses"]:
        if item["type"] == ip_address_type:
            return item["ipAddress"]
    raise ValueError("Can't find instance %s %s ip address" % (instance, ip_address_type))


DEST_INSTANCE_INFO = get_instance_info(project=DEST_PROJECT, instance=DEST_INSTANCE)
REPLICA_NAMES = DEST_INSTANCE_INFO["replicaNames"] if "replicaNames" in DEST_INSTANCE_INFO else []

if REPLICA_NAMES:
    for replica_name in REPLICA_NAMES:
        print("Deleting replica %s" % replica_name)
        operation_name = SQLADMIN_INSTANCES.delete(project=DEST_PROJECT, instance=replica_name).execute()["name"]

        operation_listed_once = False
        try:
            while SQLADMIN.operations().get(project=DEST_PROJECT, operation=operation_name).execute()[
                "status"] != "DONE":
                operation_listed_once = True
                print("Operation %s still pending, sleeping 30s..." % operation_name)
                sleep(30)
        except HttpError as http_error:
            if operation_listed_once:
                print("Operation %s not found anymore, should be done" % operation_name)
            else:
                raise http_error

backup_id = get_last_successful_backup_run_id(project=SOURCE_PROJECT, instance=SOURCE_INSTANCE)

restorebackup_body = {  # Database instance restore backup request.
    "restoreBackupContext": {
        # Database instance restore from backup context. # Parameters required to perform the restore backup operation.
        "instanceId": SOURCE_INSTANCE,  # The ID of the instance that the backup was taken from.
        "project": SOURCE_PROJECT,  # The full project ID of the source instance.
        "backupRunId": backup_id,  # The ID of the backup run to restore from.
    },
}

restore_backup_operation = SQLADMIN_INSTANCES.restoreBackup(project=DEST_PROJECT, instance=DEST_INSTANCE,
                                                            body=restorebackup_body).execute()

print("Restoring backup %s to %s" % (backup_id, DEST_INSTANCE))

while SQLADMIN.operations().get(project=DEST_PROJECT, operation=restore_backup_operation['name']).execute()[
    "status"] != "DONE":
    sleep(60)

print("Restore done")

users_update_body = {  # A Cloud SQL user resource.
    "kind": "sql#user",  # This is always sql#user.
    "name": SOURCE_USER,
    # The name of the user in the Cloud SQL instance. Can be omitted for update since it is already specified in the URL.
    "project": DEST_PROJECT,
    # The project ID of the project containing the Cloud SQL database. The Google apps domain is prefixed if applicable. Can be omitted for update since it is already specified on the URL.
    "instance": DEST_INSTANCE,
    # The name of the Cloud SQL instance. This does not include the project ID. Can be omitted for update since it is already specified on the URL.
    "host": "",
    # The host name from which the user can connect. For insert operations, host defaults to an empty string. For update operations, host is specified as part of the request URL. The host name cannot be updated after insertion.
    "password": SOURCE_USER_TEMP_PASSWORD,  # The password for the user.
}

print("Updating password for user %s" % SOURCE_USER)
SQLADMIN.users().update(project=DEST_PROJECT, instance=DEST_INSTANCE, name=SOURCE_USER,
                        body=users_update_body).execute()

print("Creating user %s" % DEST_NEW_USER)
SQLADMIN.users().insert(project=DEST_PROJECT, instance=DEST_INSTANCE,
                        body={"name": DEST_NEW_USER, "password": DEST_NEW_USER_PASSWORD}).execute()

print("Renaming database %s to %s and changing owner to %s" % (SOURCE_DATABASE_NAME, DEST_DATABASE_NAME, DEST_NEW_USER))
as_source_user_to_postgres_db_connection = connect_to_dest_instance(SOURCE_USER, SOURCE_USER_TEMP_PASSWORD, "postgres")
as_source_user_to_postgres_db_connection_cursor = as_source_user_to_postgres_db_connection.cursor()

grant_request = 'GRANT "%s" TO "%s"' % (DEST_NEW_USER, SOURCE_USER)
print(grant_request)
as_source_user_to_postgres_db_connection_cursor.execute(grant_request)

database_rename_request = 'ALTER DATABASE "%s" RENAME TO "%s"' % (SOURCE_DATABASE_NAME, DEST_DATABASE_NAME)
print(database_rename_request)
as_source_user_to_postgres_db_connection_cursor.execute(database_rename_request)

change_database_owner_request = 'ALTER DATABASE "%s" OWNER TO "%s"' % (DEST_DATABASE_NAME, DEST_NEW_USER)
print(change_database_owner_request)
as_source_user_to_postgres_db_connection_cursor.execute(change_database_owner_request)

as_source_user_to_postgres_db_connection.close()

as_source_user_to_dest_db_connection = connect_to_dest_instance(SOURCE_USER, SOURCE_USER_TEMP_PASSWORD,
                                                                DEST_DATABASE_NAME)
as_source_user_to_dest_db_connection_cursor = as_source_user_to_dest_db_connection.cursor()
as_source_user_to_dest_db_connection_cursor.execute('REASSIGN OWNED BY "%s" TO "%s"' % (SOURCE_USER, DEST_NEW_USER))
as_source_user_to_dest_db_connection.close()

as_dest_user_to_dest_db_connection = connect_to_dest_instance(DEST_NEW_USER, DEST_NEW_USER_PASSWORD, DEST_DATABASE_NAME)
as_dest_user_to_dest_db_connection_cursor = as_dest_user_to_dest_db_connection.cursor()
as_dest_user_to_dest_db_connection_cursor.execute('DROP ROLE "%s"' % SOURCE_USER)

if POST_PROCESS:
    if not DEST_DATABASE_HOST:
        DEST_DATABASE_HOST = get_instance_ip_address(DEST_PROJECT, DEST_INSTANCE, DEST_INSTANCE_IP_ADDRESS_TYPE)

    print("Emptying unneeded tables: %s" % ", ".join(TABLES_TO_EMPTY))
    for table in TABLES_TO_EMPTY:
        truncate_table_query = "TRUNCATE TABLE %s" % table
        print(truncate_table_query)
        as_dest_user_to_dest_db_connection_cursor.execute(truncate_table_query)

    environ["PGPASSWORD"] = DEST_NEW_USER_PASSWORD
    print("Starting: psql anonymize script %s" % datetime.now())
    anonymize_sql_script = open(ANONYMIZE_SQL_SCRIPT_PATH, mode='r').read()
    subprocess.run(
        ["psql", "--host", DEST_DATABASE_HOST, "--user", DEST_NEW_USER, DEST_DATABASE_NAME],
        env={"PGPASSWORD": DEST_NEW_USER_PASSWORD, "PATH": getenv("PATH")},
        input=anonymize_sql_script,
        text=True,
        check=True
    )
    print("Ended: psql anonymize script %s" % datetime.now())

    # Launch import user script
    print("Starting: user import script %s" % datetime.now())

    environ["DATABASE_URL"] = "postgresql://%s:%s@%s:%s/%s" % (
        DEST_NEW_USER, DEST_NEW_USER_PASSWORD, DEST_DATABASE_HOST, DEST_DATABASE_PORT, DEST_DATABASE_NAME)
    subprocess.run(["python3", "%s/%s" % (PCAPI_ROOT_PATH, IMPORT_USERS_SCRIPT_PATH), USERS_CSV_PATH], check=True)
    print("Ended: user import script %s" % datetime.now())

    print("Starting: disable all venue providers %s" % datetime.now())
    as_dest_user_to_dest_db_connection_cursor.execute('UPDATE venue_provider SET "isActive" = false')
    print("Ended: disable all venue providers %s" % datetime.now())

    print("Backing up %s" % DEST_INSTANCE)
    backup_info = SQLADMIN_BACKUP_RUNS.insert(project=DEST_PROJECT, instance=DEST_INSTANCE).execute()

    while SQLADMIN_BACKUP_RUNS.get(
            project=DEST_PROJECT,
            instance=DEST_INSTANCE,
            id=backup_info["backupContext"]["backupId"]
    ).execute()["status"] != "SUCCESSFUL":
        sleep(60)
    print("Backup done")

as_dest_user_to_dest_db_connection.close()

if REPLICA_NAMES:
    for replica_name in REPLICA_NAMES:
        replica_creation_request_body = {
            "masterInstanceName": DEST_INSTANCE,
            "project": DEST_PROJECT,
            "databaseVersion": DEST_INSTANCE_INFO["databaseVersion"],
            "name": replica_name,
            "region": DEST_INSTANCE_INFO["region"],
            "settings":
                {
                    "tier": DEST_INSTANCE_INFO["settings"]["tier"],
                    "settingsVersion": 0,
                }
        }
        print(SQLADMIN_INSTANCES.insert(project=DEST_PROJECT, body=replica_creation_request_body).execute())
