from scripts.check_ci_status import extract_commit_status, get_project_jobs_infos, main
import pytest
import sys
import copy

project_jobs_infos_mock =[{
    "build_parameters": {
        "CIRCLE_JOB": "tests-api"
    },
    'failed': False,
    'status': 'success',
    'committer_name': 'bobby',
    'all_commit_details': [
        {
            'branch': 'master',
            'commit': '56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b',
            'committer_name': 'bobby',
            'subject': '🚀 v40.0.9',
        }
    ],
    'vcs_revision': '56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b',
    'outcome': 'success',
    'vcs_url': 'https://github.com/betagouv/pass-culture-api'
}]

class CheckCIStatusTest:

    def when_extract_commit_status_does_not_find_commit_in_jobs(self):
        # Given
        job_name = "tests-api"
        target_commit_sha1 = "56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b"
        actual_commit_sha1 = "fake_sha1"
        incorrect_commit_project_jobs_infos_mock = copy.deepcopy(project_jobs_infos_mock)
        incorrect_commit_project_jobs_infos_mock[0]['vcs_revision'] = actual_commit_sha1

        # When
        commit_status = extract_commit_status(target_commit_sha1, incorrect_commit_project_jobs_infos_mock, job_name)

        # Then
        assert commit_status is None

    def when_extract_commit_status_does_not_find_correct_circle_job(self):
        # Given
        job_name = "deploy_api"
        target_commit_sha1 = "56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b"
        actual_circle_job = "tests-api"
        incorrect_job_project_jobs_infos_mock = copy.deepcopy(project_jobs_infos_mock)
        incorrect_job_project_jobs_infos_mock[0]['build_parameters']['CIRCLE_JOB'] = actual_circle_job


        # When
        commit_status = extract_commit_status(target_commit_sha1, incorrect_job_project_jobs_infos_mock, job_name)

        # Then
        assert commit_status is None

    def when_extract_commit_status_finds_correct_circle_job(self):
        # Given
        job_name = "tests-api"
        commit_sha1 = "56ePe4eVerbd4e9c52bce2342a0e28aa3003500f7b"

        # When
        commit_status = extract_commit_status(commit_sha1, project_jobs_infos_mock, job_name)

        # Then
        assert commit_status == "success"

    def when_get_project_jobs_infos_is_called_with_wrong_tag_name_returns_None(self, requests_mock):
        # Given
        tag_name = '1.23.4'
        requests_mock.get('https://circleci.com/api/v1.1/project/github/pass-culture/pass-culture-main/tree/' + tag_name, json=[{'job_id': '12'}], status_code=404)

        # When
        project_info = get_project_jobs_infos(tag_name)

        # Then
        assert project_info is None

    def when_get_project_jobs_infos_is_called_with_right_tag_name_returns_job_id(self, requests_mock):
        # Given
        tag_name = '1.3.4'
        requests_mock.get('https://circleci.com/api/v1.1/project/github/pass-culture/pass-culture-main/tree/' + tag_name, json=[{'job_id': '12'}], status_code=200)

        # When
        job_statuses = get_project_jobs_infos(tag_name)

        # Then
        assert job_statuses == [{'job_id': '12'}]

    def when_check_ci_is_called_without_an_argument_exits_system(self, capsys):
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

    def when_check_ci_is_called_but_finds_no_job_raises_exeption(self, mocker, capsys ):
        # Given
        commit_sha1 = 'commit_sha_12345'
        mocker.patch('scripts.check_ci_status.get_project_jobs_infos', return_value = False)

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            sys.argv = ["scripts/check_ci_status.py", commit_sha1]
            main()

        # Then
        assert pytest_wrapped_e.value.code == 1


    def when_check_ci_is_called_but_commit_has_failed_raises_system_error_exception(self, mocker, capsys ):
        # Given
        commit_sha1 = 'commit_sha_12345'
        mocker.patch('scripts.check_ci_status.get_project_jobs_infos', return_value = project_jobs_infos_mock)
        mocker.patch('scripts.check_ci_status.extract_commit_status', return_value = False)

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            sys.argv = ["scripts/check_ci_status.py", commit_sha1]
            main()

        # Then
        assert pytest_wrapped_e.value.code == 1

    def when_check_ci_is_called_and_commit_is_successful(self, mocker, capsys ):
        # Given
        commit_sha1 = 'commit_sha_12345'
        tag_name = '1.2.3'
        mocker.patch('scripts.check_ci_status.get_project_jobs_infos', return_value = project_jobs_infos_mock)
        mocker.patch('scripts.check_ci_status.extract_commit_status', return_value = "success")

        # When
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            sys.argv = ["scripts/check_ci_status.py", commit_sha1, tag_name]
            main()

        # Then
        assert pytest_wrapped_e.value.code == 0