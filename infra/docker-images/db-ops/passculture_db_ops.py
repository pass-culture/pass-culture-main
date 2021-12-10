import random
import string

from cloudsqlpostgresinstance import CloudSQLPostgresInstance
from datetime import datetime
from os import getenv
import subprocess

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def rename_database_and_change_owner(
    instance: CloudSQLPostgresInstance,
    old_database_name: str,
    new_database_name: str,
    owner: str,
    owner_password: str,
    new_owner: str,
    new_owner_password
):
    instance.connect(username=owner, password=owner_password, database="postgres")
    instance.rename_database(old_database_name=old_database_name, new_database_name=new_database_name)
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


def import_users():
    print("Starting: user import script %s" % datetime.now())
    subprocess.run(["python3",  getenv("IMPORT_USERS_SCRIPT_PATH"), getenv("USERS_CSV_PATH")], check=True)
    print("Ended: user import script %s" % datetime.now())


def anonymize(database_url: str):
    print("Starting: psql anonymize script %s" % datetime.now())
    anonymize_sql_script = open(getenv("ANONYMIZE_SQL_SCRIPT_PATH"), mode='r').read()
    subprocess.run(
        ["psql", database_url],
        env={"PATH": getenv("PATH")},
        input=anonymize_sql_script,
        text=True,
        check=True
    )
    print("Ended: psql anonymize script %s" % datetime.now())


def empty_tables(instance: CloudSQLPostgresInstance, tables: list[str]):
    print("Emptying unneeded tables: %s" % ", ".join(tables))
    for table in tables:
        truncate_table_query = "TRUNCATE TABLE %s" % table
        print(truncate_table_query)
        instance.execute_query(truncate_table_query)


def build_database_url(database_host: str, database_port: int, database_name: str, username: str, password: str):
    return "postgresql://%s:%s@%s:%s/%s?keepalives=1" % (username, password, database_host, database_port, database_name)


def run_flask_command(*args: str):
    print("Starting: flask %s %s" % (' '.join(args), datetime.now()))
    subprocess.run(["flask"] + list(args), check=True)
    print("Ended: flask %s %s" % (' '.join(args), datetime.now()))