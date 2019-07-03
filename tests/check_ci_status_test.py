from scripts.check_ci_status import extract_commit_status
from scripts.check_ci_status import get_project_jobs_infos, main
import pytest
import requests
import requests_mock
import sys

project_jobs_infos =[{
    'failed': False,
    'status': 'success',
    'committer_name': 'bobby',
    'all_commit_details': [
        {
            'branch': 'master',
            'commit': '56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b',
            'committer_name': 'bobby',
            'subject': '🚀 v37.0.2',
        }
    ],
    'outcome': 'success',
    'vcs_url': 'https://github.com/betagouv/pass-culture-api'
}]

project_jobs_infos_whitout_hash =[{
    'failed': False,
    'status': 'success',
    'committer_name': 'bobby',
    'all_commit_details': [
        {
            'branch': 'master',
            'commit': 'fake000ed4bd4e9c52bce2342a0e28aa30035009S',
            'committer_name': 'bobby',
            'subject': 'fix linter',
        }
    ],
    'outcome': 'success',
    'vcs_url': 'https://github.com/betagouv/pass-culture-api'
}]

class CheckCIStatusTest:


    def when_extract_commit_status_is_called_with_non_existing_sha1(self):

        # Given
        commit_sha1 = "fake_sha1"

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            extract_commit_status(commit_sha1, project_jobs_infos_whitout_hash)

        # Then
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def when_extract_commit_status_is_called_with_existing_sha1(self):

        # Given
        commit_sha1 = "56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b"

        # When
        commit_status = extract_commit_status(commit_sha1, project_jobs_infos)

        # Then
        assert commit_status == "success"

    def when_get_project_jobs_infos_is_called_with_wrong_project_name(self, requests_mock):

        # Given
        project_name = "wrong_project_name_987"
        requests_mock.get('https://circleci.com/api/v1.1/project/github/betagouv/' + project_name + '/tree/master', json=[{'job_id': '12'}], status_code=404)

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            get_project_jobs_infos(project_name)

        # Then
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def when_get_project_jobs_infos_is_called_with_right_project_name(self, requests_mock):

        # Given
        project_name = "pass-culture-api"
        requests_mock.get('https://circleci.com/api/v1.1/project/github/betagouv/' + project_name + '/tree/master', json=[{'job_id': '12'}], status_code=200)

        # When
        job_statuses = get_project_jobs_infos(project_name)

        # Then
        assert job_statuses == [{'job_id': '12'}]

    def when_check_ci_is_called_whitout_an_argument(self, capsys ):

        # Given
        sys.argv = ["scripts/check_ci_status.py"]

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            sys.argv = ["scripts/check_ci_status.py"]
            main()
        out, err = capsys.readouterr()

        # Then
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

    def when_check_ci_is_called_whith_argument_(self, capsys ):

        # Given
        commit_sha1 = 'commit_sha_12345'

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            sys.argv = ["scripts/check_ci_status.py", commit_sha1]
            main()

        # Then
        assert pytest_wrapped_e.value.code == 0
