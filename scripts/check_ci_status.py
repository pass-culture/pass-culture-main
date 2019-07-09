import sys
import requests
from typing import List, Optional

def extract_commit_status(commit_sha1: str, project_jobs_infos: str, test_name:str) -> Optional[str]:
    for job in project_jobs_infos :
        if job['build_parameters']['CIRCLE_JOB'] == test_name and job['all_commit_details'][0]['commit'] == commit_sha1 :
            return job['status']
    return None

def get_project_jobs_infos(branch_name: str) -> Optional[str]:
    project_url = 'https://circleci.com/api/v1.1/project/github/betagouv/pass-culture-main/tree/' + branch_name
    response = requests.get(project_url)
    if response.status_code != 200 :
        print('Error while requesting CircleCi. Return Code :', response.status_code)
        return None
    return response.json()


def main():
    project_name = "pass-culture-main"
    tests_names = ["tests-script-pc", "tests-api", "tests-webapp", "tests-pro"]

    if len(sys.argv) < 3:
        print('Error : Scripts needs to be called with 2 arguments, a commit hash and a branch name')
        sys.exit(1)

    commit_sha1 = sys.argv[1]
    branch_name = sys.argv[2]

    project_jobs_infos = get_project_jobs_infos(branch_name)

    if not project_jobs_infos:
        print('Error : Could not find projects jobs informations')
        sys.exit(1)

    for test_name in tests_names:
        commit_status = extract_commit_status(commit_sha1, project_jobs_infos, test_name)

        if commit_status != "success" :
            print('Error, job ', test_name, " has status ", commit_status, "for commit ", commit_sha1)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

