import sys
import requests

def extract_commit_status(commit_sha1, project_jobs_infos, test_name):
    for job in project_jobs_infos :
        if job['build_parameters']['CIRCLE_JOB'] == test_name and job['all_commit_details'][0]['commit'] == commit_sha1 :
            return job['status']

    print('Target commit details not found in project\'s jobs')
    return False

def get_project_jobs_infos(project_name):
    project_url = 'https://circleci.com/api/v1.1/project/github/betagouv/' + project_name + '/tree/master'
    response = requests.get(project_url)
    if response.status_code != 200 :
        print('Error while requesting CircleCi. Return Code :', response.status_code)
        sys.exit(1)
    return response.json()


def main():
    project_name = "pass-culture-main"
    test_names = ["tests-script-pc", "tests-api", "tests-webapp", "tests-pro"]

    if len(sys.argv) < 2:
        sys.exit(1)

    commit_sha1 = sys.argv[1]
    project_jobs_infos = get_project_jobs_infos(project_name)

    if not project_jobs_infos:
        sys.exit(1)

    for test_name in test_names:
        commit_status = extract_commit_status(commit_sha1, project_jobs_infos, test_name)

        if commit_status != "success" :
            print('Error, job ', test_name, " has status ", commit_status, "for commit ", commit_sha1)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

