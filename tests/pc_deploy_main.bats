#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock

debug_mock() {
  # Debug
  # Use the below line if you actually want to see all the arguments the function used to call the 'stub'
  index=1
  while [ "$index" -le $(mock_get_call_num ${mock_git}) ]
  do
    echo "# call_args: " $(mock_get_call_args ${mock_git} "$index") >&3
    index=$((index+1))
  done
  
  index=1
  while [ "$index" -le $(mock_get_call_num ${mock_curl}) ]
  do
    echo "# call_args: " $(mock_get_call_args ${mock_curl} "$index") >&3
    index=$((index+1))
  done

  index=1
  while [ "$index" -le $(mock_get_call_num ${mock_xdg}) ]
  do
    echo "# call_args: " $(mock_get_call_args ${mock_xdg} "$index") >&3
    index=$((index+1))
  done
}

mocked_command_git=""
mock_git=""
mock_path_git=""
mock_file_git=""

mocked_command_curl=""
mock_curl=""
mock_path_curl=""
mock_file_curl=""

mocked_command_xdg=""
mock_xdg=""
mock_path_xdg=""
mock_file_xdg=""

setup(){
    mocked_command_git="git"
    mock_git="$(mock_create)"
    mock_path_git="${mock_git%/*}"
    mock_file_git="${mock_git##*/}"
    ln -sf "${mock_path_git}/${mock_file_git}" "${mock_path_git}/${mocked_command_git}"
    PATH="${mock_path_git}:$PATH"
    
    mocked_command_curl="curl"
    mock_curl="$(mock_create)"
    mock_path_curl="${mock_curl%/*}"
    mock_file_curl="${mock_curl##*/}"
    ln -sf "${mock_path_curl}/${mock_file_curl}" "${mock_path_curl}/${mocked_command_curl}"
    PATH="${mock_path_curl}:$PATH"  
  
    mocked_command_xdg="xdg-open"
    mock_xdg="$(mock_create)"
    mock_path_xdg="${mock_xdg%/*}"
    mock_file_xdg="${mock_xdg##*/}"
    ln -sf "${mock_path_xdg}/${mock_file_xdg}" "${mock_path_xdg}/${mocked_command_xdg}"
    PATH="${mock_path_xdg}:$PATH"
}

teardown(){
    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_git}/${mocked_command_git}"
    PATH="${PATH/${mock_path_git}:/}"

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_curl}/${mocked_command_curl}"
    PATH="${PATH/${mock_path_curl}:/}"

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_xdg}/${mocked_command_xdg}"
    PATH="${PATH/${mock_path_xdg}:/}"
}

@test "Deploy should not be run if current ENV is development" {
    # Given
    expected_output='Deploy cannot be run on the local environment. Use (for example) "pc -e staging -t X.Y.Z deploy".'

    # When
    run pc deploy

    # Then
    echo "Status: ""$status"
    [ "$status" -eq 3 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [ "${lines[0]}" == "$expected_output" ]
}

@test "Deploy on unknown environment is not allowed" {
    # Given
    environment='unexisting-env'
    expected_output='Can only deploy in datalake, staging, integration and production'

    # When
    run pc -e "$environment" deploy

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy on known environment but with no tag is not allowed" {
    # Given
    environment='staging'
    expected_output='ERROR: You need to specify an existing tag to deploy'

    # When
    run pc -e "$environment" deploy

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy not working with malformed tag" {
    # Given
    environment='staging'
    non_valid_tag='bats-tests'
    expected_output='tag format should be Semantic Versioning compliant x.x.x'

    # When
    run pc -e "$environment" -t "$non_valid_tag" deploy

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy cannot deploy not tagged version" {
    # Given
    index=0
    expected_output='ERROR: You need to specify an existing remote tag to deploy'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # git fetch
    mock_set_output "${mock_git}" "fetch" 2
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 3
    # git reset --hard origin/master || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull master" 4
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git reset --hard origin/staging || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 8
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 9
    # git reset --hard origin/integration || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 10
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git reset --hard origin/production || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 14
    # git ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock_git}" "" 15
    # git checkout current branch
    mock_set_output "${mock_git}" "checkout current branch" 16

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]

    # When
    run pc -e staging -t 0.0.0 deploy

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 16 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}

@test "Deploy in production not working when commits are not in staging" {
    # Given
    index=0
    expected_output='ERROR: Can only deploy in production commits that are also deployed in staging'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # git fetch
    mock_set_output "${mock_git}" "fetch" 2
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 3
    # git reset --hard origin/master || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull master" 4
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git reset --hard origin/staging || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 8
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 9
    # git reset --hard origin/integration || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 10
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git reset --hard origin/production || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 14
    # git ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock_git}" "v0.0.0" 15
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock_git}" "checkout TAG_NAME" 16
    # git submodule update
    mock_set_output "${mock_git}" "submodule update" 17
    # git log -n 1 --pretty=format:%H
    mock_set_output "${mock_git}" "commit_hash" 18
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock_git}" "commit_hash_staging" 19
    # git checkout current branch
    mock_set_output "${mock_git}" "checkout current branch" 20

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]

    # When
    run bash -c "echo 'y' | pc -e production -t 0.0.0 deploy"

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 20 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}


@test "Deploy in production works with commits that are also in staging" {
    # Given
    index=0
    expected_output='/!\\ You just deployed to production. Was the version also delivered to integration ?'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # git fetch
    mock_set_output "${mock_git}" "fetch" 2
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 3
    # git reset --hard origin/master || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull master" 4
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git reset --hard origin/staging || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 8
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 9
    # git reset --hard origin/integration || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 10
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git reset --hard origin/production || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 14
    # git ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock_git}" "v0.0.0" 15
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock_git}" "checkout TAG_NAME" 16
    # git submodule update
    mock_set_output "${mock_git}" "submodule update" 17
    # git log -n 1 --pretty=format:%H
    mock_set_output "${mock_git}" "commit_hash" 18
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock_git}" "commit_hash" 19
    # git push -f origin HEAD:"$ENV"
    mock_set_output "${mock_git}" "push origin HEAD" 20
    # git checkout current branch
    mock_set_output "${mock_git}" "Exit success !" 21

    # curl https://circleci.com/api/v1.1/project/github/betagouv/pass-culture-main/tree/production
    mock_set_output "${mock_curl}" '[{ "vcs_revision" : "commit_hash",
        "workflows" : {
            "job_name" : "job_name",
            "job_id" : "job_id",
            "workflow_id" : "workflow_id",
            "workspace_id" : "workspace_id",
            "upstream_job_ids" : [ ],
            "upstream_concurrency_map" : { },
            "workflow_name" : "commit"
        }
    },{
    }]' 1

    # xdg-open "https://circleci.com/workflow-run/$workflow_id"
    mock_set_output "${mock_xdg}" "link opened" 1

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]
    [[ "$(readlink -e $(which curl))" == "$(readlink -e ${mock_curl})" ]]
    [[ "$(readlink -e $(which xdg-open))" == "$(readlink -e ${mock_xdg})" ]]

    # When
    run bash -c "echo 'y' | pc -e production -t 0.0.0 deploy"

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    echo "Number of calls: $(mock_get_call_num ${mock_curl})"
    echo "Number of calls: $(mock_get_call_num ${mock_xdg})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 21 ]]
    [[ "$(mock_get_call_num ${mock_curl})" -eq 1 ]]
    [[ "$(mock_get_call_num ${mock_xdg})" -eq 1 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}


@test "Deploy in production retry to access build status when commit not yet in circleci api" {
    # Given
    index=0
    expected_output='/!\\ You just deployed to production. Was the version also delivered to integration ?'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # git fetch
    mock_set_output "${mock_git}" "fetch" 2
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 3
    # git reset --hard origin/master || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull master" 4
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git reset --hard origin/staging || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 8
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 9
    # git reset --hard origin/integration || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 10
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git reset --hard origin/production || exit_error_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git submodule update || exit_error_restoring_branch
    mock_set_output "${mock_git}" "submodule update" 14
    # git ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock_git}" "v0.0.0" 15
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock_git}" "checkout TAG_NAME" 16
    # git submodule update
    mock_set_output "${mock_git}" "submodule update" 17
    # git log -n 1 --pretty=format:%H
    mock_set_output "${mock_git}" "commit_hash" 18
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock_git}" "commit_hash" 19
    # git push -f origin HEAD:"$ENV"
    mock_set_output "${mock_git}" "push origin HEAD" 20
    # git checkout current branch
    mock_set_output "${mock_git}" "Exit success !" 21

    # curl https://circleci.com/api/v1.1/project/github/betagouv/pass-culture-main/tree/production
    mock_set_output "${mock_curl}" '[{ "vcs_revision" : "other_commit_hash",
        "workflows" : {
            "job_name" : "job_name",
            "job_id" : "job_id",
            "workflow_id" : "workflow_id",
            "workspace_id" : "workspace_id",
            "upstream_job_ids" : [ ],
            "upstream_concurrency_map" : { },
            "workflow_name" : "commit"
        }
    },{
    }]' 1
    # curl https://circleci.com/api/v1.1/project/github/betagouv/pass-culture-main/tree/production
    mock_set_output "${mock_curl}" '[{ "vcs_revision" : "commit_hash",
        "workflows" : {
            "job_name" : "job_name",
            "job_id" : "job_id",
            "workflow_id" : "workflow_id",
            "workspace_id" : "workspace_id",
            "upstream_job_ids" : [ ],
            "upstream_concurrency_map" : { },
            "workflow_name" : "commit"
        }
    },{
    }]' 2

    # xdg-open "https://circleci.com/workflow-run/$workflow_id"
    mock_set_output "${mock_xdg}" "link opened" 1

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]
    [[ "$(readlink -e $(which curl))" == "$(readlink -e ${mock_curl})" ]]
    [[ "$(readlink -e $(which xdg-open))" == "$(readlink -e ${mock_xdg})" ]]

    # When
    run bash -c "echo 'y' | pc -e production -t 0.0.0 deploy"

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    echo "Number of calls: $(mock_get_call_num ${mock_curl})"
    echo "Number of calls: $(mock_get_call_num ${mock_xdg})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 21 ]]
    [[ "$(mock_get_call_num ${mock_curl})" -eq 2 ]]
    [[ "$(mock_get_call_num ${mock_xdg})" -eq 1 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}
