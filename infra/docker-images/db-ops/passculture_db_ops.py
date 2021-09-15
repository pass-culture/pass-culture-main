from cloudsqlpostgresinstance import CloudSQLPostgresInstance
from datetime import datetime
import env_vars
import os
import subprocess

def transform_database(
    instance: CloudSQLPostgresInstance,
    old_database_name: str,
    new_database_name: str,
    owner: str,
    owner_password: str,
    new_owner: str,
    new_owner_password
):
    instance.connect(username=owner, password=owner_password, database="postgres")
    instance.rename_database(old_database_name=old_database_name, new_name=new_database_name)
    instance.change_database_owner(database=new_database_name, current_owner=owner, new_owner=new_owner)
    instance.disconnect()

    instance.connect(username=owner, password=owner_password, database=new_database_name)
    instance.reassign_owned(owner, new_owner)
    instance.disconnect()

    instance.connect(username=new_owner, password=new_owner_password, database=new_database_name)
    instance.drop_role(role=owner)
    instance.disconnect()


def disable_venue_providers(instance: CloudSQLPostgresInstance):
    print("Starting: disable all venue providers %s" % datetime.now())
    instance.execute_query('UPDATE venue_provider SET "isActive" = false')
    print("Ended: disable all venue providers %s" % datetime.now())


def import_users(database_host: str, database_port: int, database_name: str, username: str, password: str):
    print("Starting: user import script %s" % datetime.now())
    os.environ["DATABASE_URL"] = "postgresql://%s:%s@%s:%s/%s" % (username, password, database_host, database_port, database_name)
    subprocess.run(["python3", "%s/%s" % (env_vars.PCAPI_ROOT_PATH, env_vars.IMPORT_USERS_SCRIPT_PATH), env_vars.USERS_CSV_PATH], check=True)
    print("Ended: user import script %s" % datetime.now())


def anonymize(database_host: str, database_port: int, database_name: str, username: str, password: str):
    print("Starting: psql anonymize script %s" % datetime.now())
    anonymize_sql_script = open(env_vars.ANONYMIZE_SQL_SCRIPT_PATH, mode='r').read()
    subprocess.run(
        ["psql", "--host", database_host, "--user", username, database_name],
        env={"PGPASSWORD": password, "PATH": os.getenv("PATH")},
        input=anonymize_sql_script,
        text=True,
        check=True
    )
    print("Ended: psql anonymize script %s" % datetime.now())


def empty_tables(instance: CloudSQLPostgresInstance, tables: list[str]):
    print("Emptying unneeded tables: %s" % ", ".join(tables))
    for table in env_vars.TABLES_TO_EMPTY:
        truncate_table_query = "TRUNCATE TABLE %s" % table
        print(truncate_table_query)
        instance.execute_query(truncate_table_query)


def post_process(instance: CloudSQLPostgresInstance, username: str, password: str, database_name: str, database_host: str, database_port: int):
    empty_tables(instance=instance, tables=env_vars.TABLES_TO_EMPTY)

    anonymize(
        database_host=database_host,
        database_port=database_port,
        database_name=database_name,
        username=username,
        password=password
    )

    import_users(
        database_host=database_host,
        database_port=database_port,
        database_name=database_name,
        username=username,
        password=password
    )

    disable_venue_providers(instance)

