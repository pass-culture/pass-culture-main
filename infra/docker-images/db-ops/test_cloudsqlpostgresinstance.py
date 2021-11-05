import unittest
from unittest.mock import Mock, patch
from cloudsqlpostgresinstance import CloudSQLPostgresInstance

class TestCloudSQLPostgresInstance(unittest.TestCase):
    def setUp(self):
        self.sqladmin_backup_runs_service = Mock()
        self.sqladmin_databases_service = Mock()
        self.sqladmin_instances_service = Mock()
        self.sqladmin_operations_service = Mock()
        self.sqladmin_users_service = Mock()

        self.instance = CloudSQLPostgresInstance(
            name = "test-instance",
            project = "test-project",
            region = "test-region",
            sqladmin_backup_runs_service = self.sqladmin_backup_runs_service,
            sqladmin_databases_service = self.sqladmin_databases_service,
            sqladmin_instances_service = self.sqladmin_instances_service,
            sqladmin_operations_service = self.sqladmin_operations_service,
            sqladmin_users_service = self.sqladmin_users_service,
        )

        self.fake_sql_backup_run_backup_context = {
            "backupContext": {
                "backupId": "fake-id"
            }
        }
        self.fake_running_sql_backup_run_status = { "status": "RUNNING", **self.fake_sql_backup_run_backup_context }
        self.fake_successful_sql_backup_run_status = { "status": "SUCCESSFUL", **self.fake_sql_backup_run_backup_context }
        self.fake_failed_sql_backup_run_status = {"status": "FAILED", **self.fake_sql_backup_run_backup_context }

    @patch("cloudsqlpostgresinstance.sleep")
    def test_backup_does_not_raise_error_on_success(self, sleep_mock):
        self.sqladmin_backup_runs_service.insert.return_value.execute.return_value = self.fake_running_sql_backup_run_status

        self.sqladmin_backup_runs_service.get.return_value.execute.side_effect = [
            self.fake_running_sql_backup_run_status,
            self.fake_successful_sql_backup_run_status,
            self.fake_successful_sql_backup_run_status,
        ]

        self.instance.backup()
        self.sqladmin_backup_runs_service.insert.assert_called_once_with(instance = "test-instance", project = "test-project")
        self.sqladmin_backup_runs_service.insert.return_value.execute.assert_called_once()
        self.sqladmin_backup_runs_service.get.return_value.execute.assert_called()

    @patch("cloudsqlpostgresinstance.sleep")
    def test_backup_raises_error_on_failure(self, sleep_mock):
        self.sqladmin_backup_runs_service.insert.return_value.execute.return_value = self.fake_running_sql_backup_run_status

        self.sqladmin_backup_runs_service.get.return_value.execute.side_effect = [
            self.fake_running_sql_backup_run_status,
            self.fake_failed_sql_backup_run_status,
            self.fake_failed_sql_backup_run_status,
        ]

        self.assertRaises(RuntimeError, self.instance.backup)
        self.sqladmin_backup_runs_service.insert.assert_called_once_with(instance = "test-instance", project = "test-project")
        self.sqladmin_backup_runs_service.insert.return_value.execute.assert_called_once()
        self.sqladmin_backup_runs_service.get.return_value.execute.assert_called()

if __name__ == '__main__':
    unittest.main()
