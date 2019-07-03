import sys
import requests

project_names

def extract_commit_status(commit_sha1, project_jobs_infos):
    print(commit_sha1)
    print(project_jobs_infos[0]['status'])
    for job in project_jobs_infos :
        print(job['all_commit_details'][0]['commit'])
        if job['all_commit_details'][0]['commit'] == commit_sha1 :
            return job['status']

    print('Target commit details not found in project\'s jobs')
    sys.exit(1)

def get_project_jobs_infos(project_name):
    project_url = 'https://circleci.com/api/v1.1/project/github/betagouv/' + project_name + '/tree/master'
    response = requests.get(project_url)
    if response.status_code != 200 :
        print('Error while requesting CircleCi. Return Code :', response.status_code)
        sys.exit(1)
    return response.json()


def main():
    if len(sys.argv) > 1:
        commit_sha1 = sys.argv[1]
        print("salut", commit_sha1)
        check_ci_status(commit_sha1)

    sys.exit(1)


if __name__ == "__main__":
    main()

