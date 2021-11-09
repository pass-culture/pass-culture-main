from datetime import datetime
from time import sleep
from typing import Callable

from googleapiclient import discovery

from google.cloud.sql.connector import connector
from googleapiclient.errors import HttpError


class CloudSQLPostgresInstanceFactory:
    __initialized = False
    __sqladmin_service = None
    __sqladmin_backup_runs_service = None
    __sqladmin_databases_service = None
    __sqladmin_instances_service = None
    __sqladmin_operations_service = None
    __sqladmin_users_service = None

    @staticmethod
    def init():
        CloudSQLPostgresInstanceFactory.__sqladmin_service = discovery.build('sqladmin', 'v1beta4')
        CloudSQLPostgresInstanceFactory.__sqladmin_backup_runs_service = CloudSQLPostgresInstanceFactory.__sqladmin_service.backupRuns()
        CloudSQLPostgresInstanceFactory.__sqladmin_databases_service = CloudSQLPostgresInstanceFactory.__sqladmin_service.databases()
        CloudSQLPostgresInstanceFactory.__sqladmin_instances_service = CloudSQLPostgresInstanceFactory.__sqladmin_service.instances()
        CloudSQLPostgresInstanceFactory.__sqladmin_users_service = CloudSQLPostgresInstanceFactory.__sqladmin_service.users()
        CloudSQLPostgresInstanceFactory.__sqladmin_operations_service = CloudSQLPostgresInstanceFactory.__sqladmin_service.operations()
        CloudSQLPostgresInstanceFactory.initialized = True

    @staticmethod
    def create(name: str, project: str, region: str):
        if not CloudSQLPostgresInstanceFactory.__initialized:
            CloudSQLPostgresInstanceFactory.init()

        return CloudSQLPostgresInstance(
            name=name,
            project=project,
            region=region,
            sqladmin_backup_runs_service=CloudSQLPostgresInstanceFactory.__sqladmin_backup_runs_service,
            sqladmin_databases_service=CloudSQLPostgresInstanceFactory.__sqladmin_databases_service,
            sqladmin_operations_service=CloudSQLPostgresInstanceFactory.__sqladmin_operations_service,
            sqladmin_instances_service=CloudSQLPostgresInstanceFactory.__sqladmin_instances_service,
            sqladmin_users_service=CloudSQLPostgresInstanceFactory.__sqladmin_users_service,
        )

class CloudSQLPostgresInstance:
    def __init__(self, project: str, name: str, region: str, sqladmin_backup_runs_service,
                 sqladmin_databases_service, sqladmin_instances_service,
                 sqladmin_operations_service, sqladmin_users_service):
        self.name = name
        self.project = project
        self.region = region
        self.sqladmin_backup_runs_service = sqladmin_backup_runs_service
        self.sqladmin_databases_service = sqladmin_databases_service
        self.sqladmin_instances_service = sqladmin_instances_service
        self.sqladmin_operations_service = sqladmin_operations_service
        self.sqladmin_users_service = sqladmin_users_service
        self.replica_names_backup = []
        self.connection = None
        self.connection_cursor = None

    def connect(self, username: str, password: str, database: str, autocommit: bool = True,
                use_iam_auth: bool = False):
        self.connection = connector.connect(
            "%s:%s:%s" % (self.project, self.region, self.name),
            "pg8000",
            user=username,
            password=password,
            db=database,
            enable_iam_auth=use_iam_auth,
        )
        # Execute a query
        self.connection.autocommit = autocommit
        self.connection_cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    def backup(self):
        print("Backing up %s" % self.name)

        operation = self.sqladmin_backup_runs_service.insert(
            project=self.project,
            instance=self.name
        ).execute()

        get_backup_operation = lambda: self.sqladmin_backup_runs_service.get(
                                    project=self.project,
                                    instance=self.name,
                                    id=operation["backupContext"]["backupId"]
                                ).execute()

        self.wait_for_operation(
            check_if_operation_done_function= lambda: get_backup_operation()["status"] not in ["SUCCESSFUL", "FAILED"],
            operation_id=operation["backupContext"]["backupId"],
            check_interval=60
        )

        operation = get_backup_operation()

        if operation["status"] != "SUCCESSFUL":
            raise RuntimeError("Backup failed")

        print("Backup done")

    def create_database(self, database_name: str):
        print("Creating database %s" % database_name)
        return self.sqladmin_databases_service.insert(
            project=self.project, instance=self.name,
            body={"name": database_name}
        ).execute()

    def drop_database(self, database_name: str):
        return self.sqladmin_instances_service.delete(
            project=self.project,
            instance=self.name,
            database=database_name
        )

    def reassign_owned(self, by: str, to: str):
        reassign_owned_request = 'REASSIGN OWNED BY "%s" TO "%s"' % (by, to)
        print(reassign_owned_request)
        self.execute_query(reassign_owned_request)

    def change_database_owner(self, database: str, current_owner: str, new_owner: str):
        grant_request = 'GRANT "%s" TO "%s"' % (new_owner, current_owner)
        print(grant_request)
        self.execute_query(grant_request)

        change_database_owner_request = 'ALTER DATABASE "%s" OWNER TO "%s"' % (
            database, new_owner)
        print(change_database_owner_request)
        self.execute_query(change_database_owner_request)

    def drop_role(self, role: str):
        drop_role_request = 'DROP ROLE "%s"' % role
        print(drop_role_request)
        self.execute_query(drop_role_request)

    def rename_database(self, old_database_name: str, new_database_name: str):
        database_rename_request = 'ALTER DATABASE "%s" RENAME TO "%s"' % (old_database_name, new_database_name)
        print(database_rename_request)
        self.execute_query(database_rename_request)

    def get_info(self):
        return self.sqladmin_instances_service.get(project=self.project, instance=self.name).execute()



    def get_last_successful_backup_run_id(self) -> str:
        """
        This function returns the backupRunId (that has a successful status)
        If there are no successful backupRun the function throws an exception
        """
        backup_runs = self.sqladmin_backup_runs_service.list(
            project=self.project,
            instance=self.name
        ).execute()['items']

        successful_backup_runs = list(
            filter(lambda backup_run: backup_run['status'] == "SUCCESSFUL", backup_runs)
        )

        if not successful_backup_runs:
            raise LookupError("Can't find a successful backup")

        print(
            "Last successful backup id %s from %s" %
            (
                successful_backup_runs[0]["id"],
                datetime.strptime(successful_backup_runs[0]["endTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            )
        )

        return successful_backup_runs[0]["id"]

    def create_replica(self, replica_name: str):
        instance_info = self.get_info()

        print("Creating replica %s" % replica_name)
        operation = self.sqladmin_instances_service.insert(
            project=self.project,
            body={
                "masterInstanceName": self.name,
                "databaseVersion": instance_info["databaseVersion"],
                "name": replica_name,
                "region": instance_info["region"],
                "settings": {"tier": instance_info["settings"]["tier"]}
            }
        ).execute()


        self.wait_for_operation(
            check_if_operation_done_function=lambda: self.is_sqladmin_operation_done(operation=operation),
            operation_id=operation["name"],
            check_interval=30
        )

        operation = self.get_sqladmin_operation(name=operation["name"])
        if "error" in operation:
            raise RuntimeError("Failed to create replica %s: %s" % (replica_name, operation["error"]))

        print("Replica %s created" % replica_name)


    def delete_replica(self, replica_name: str):
        print("Deleting replica %s" % replica_name)
        operation_name = self.sqladmin_instances_service.delete(
            project=self.project,
            instance=replica_name
        ).execute()["name"]

        # not using wait_for_operation here since the operation disappears when it's done
        operation_listed_once = False
        try:
            while self.sqladmin_operations_service.get(
                    project=self.project,
                    operation=operation_name
            ).execute()["status"] != "DONE":
                operation_listed_once = True
                print("Operation %s still pending, sleeping 30s..." % operation_name)
                sleep(30)
        except HttpError as http_error:
            if operation_listed_once:
                print("Operation %s not found anymore, should be done" % operation_name)
            else:
                raise http_error

    def get_replica_names(self) -> list[str]:
        instance_info = self.get_info()
        return instance_info["replicaNames"] if "replicaNames" in instance_info else []

    def get_ip_address(self, ip_address_type: str) -> str:
        if ip_address_type == "PUBLIC":
            ip_address_type = "PRIMARY"
        for item in self.get_info()["ipAddresses"]:
            if item["type"] == ip_address_type:
                return item["ipAddress"]
        raise ValueError("Can't find instance %s %s ip address" % (self.name, ip_address_type))

    def restore_backup(self, backup_instance_id: str, backup_instance_project: str, backup_id: str):
        print("Restoring backup %s to %s" % (backup_id, self.name))

        restorebackup_body = {
            "restoreBackupContext": {
                "instanceId": backup_instance_id,
                "project": backup_instance_project,
                "backupRunId": backup_id,
            },
        }

        operation = self.sqladmin_instances_service.restoreBackup(
            project=self.project,
            instance=self.name,
            body=restorebackup_body
        ).execute()

        self.wait_for_operation(
            check_if_operation_done_function=lambda: self.is_sqladmin_operation_done(operation=operation),
            operation_id=operation["name"],
            check_interval=60
        )

        operation = self.get_sqladmin_operation(name=operation["name"])
        if "error" in operation:
            raise RuntimeError("Failed to restore backup %s: %s" % (backup_id, operation["error"]))

        print("Restore done")

    def update_user_password(self, username: str, password: str):
        print("Updating password for user %s" % username)
        return self.sqladmin_users_service.update(
            project=self.project,
            instance=self.name,
            name=username,
            body={"password": password}
        ).execute()

    def create_user(self, username: str, password: str):
        print("Creating user %s" % username)
        return self.sqladmin_users_service.insert(
            project=self.project,
            instance=self.name,
            body={"name": username, "password": password}
        ).execute()

    def import_dump(self, target_database: str, dump_uri: str, import_user: str):
        return self.sqladmin_instances_service.import_(
            project=self.project,
            instance=self.name,
            body={
                "importContext": {
                    "database": target_database,
                    "fileType": "SQL",
                    "importUser": import_user,
                    "uri": dump_uri
                }
            }
        ).execute()

    def export_dump(self, database_name: str, dump_uri: str):
        print("Exporting database %s to %s" % (database_name, dump_uri))
        operation = self.sqladmin_instances_service.export(
            project=self.project,
            instance=self.name,
            body={
                "exportContext": {
                    "databases": [database_name],
                    "fileType": "SQL",
                    "uri": dump_uri
                }
            }
        ).execute()

        self.wait_for_operation(
            check_if_operation_done_function=lambda: self.is_sqladmin_operation_done(operation=operation),
            operation_id=operation["name"],
            check_interval=10
        )

        operation = self.get_sqladmin_operation(name=operation["name"])
        if "error" in operation:
            raise RuntimeError("Failed to export dump of %s to %s: %s" % (database_name, dump_uri, operation["error"]))

        print("Ended: Exporting database %s to %s" % (database_name, dump_uri))

    def get_sqladmin_operation(self, name):
        return self.sqladmin_operations_service.get(
            project=self.project,
            operation=name
        ).execute()

    def is_sqladmin_operation_done(self, operation):
        return self.get_sqladmin_operation(operation["name"])["status"] == "DONE"

    @staticmethod
    def wait_for_operation(check_if_operation_done_function: Callable, operation_id: str, check_interval: int):
        while not check_if_operation_done_function():
            print("Operation %s still pending, sleeping %ds..." % (operation_id, check_interval))
            sleep(check_interval)

    def execute_query(self, query):
        self.connection_cursor.execute(query)
