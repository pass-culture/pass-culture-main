#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock
#load test-utils

#TODO: mettre dans utils
debug_mock() {
  # Debug
  # Use the below line if you actually want to see all the arguments the function used to call the 'stub'
  index=1
  while [ "$index" -le $(mock_get_call_num ${mock}) ]
  do
    echo "# call_args: " $(mock_get_call_args ${mock} "$index") >&3
    index=$((index+1))
  done
}

mocked_command=""
mock=""
mock_path=""
mock_file=""

setup(){
    mocked_command="git"
    mock="$(mock_create)"
    mock_path="${mock%/*}"
    mock_file="${mock##*/}"
    ln -sf "${mock_path}/${mock_file}" "${mock_path}/${mocked_command}"
    PATH="${mock_path}:$PATH"
}

teardown(){
    # Cleanup our stub and fixup the PATH
    unlink "${mock_path}/${mocked_command}"
    PATH="${PATH/${mock_path}:/}"
}

@test "Deploy-backend should not be run if current ENV is development" {
    # Given
    expected_output='Deploy backend cannot be run on the local environment. Use (for example) "pc -e staging -t X.Y.Z deploy-backend".'

    # When
    run pc deploy-backend

    # Then
    echo "Status: ""$status"
    [ "$status" -eq 3 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [ "${lines[0]}" == "$expected_output" ]
}

@test "Deploy-backend on unknown environment is not allowed" {
    # Given
    environment='unexisting-env'
    expected_output='Can only deploy-backend in staging, demo, integration and production'

    # When
    run pc -e "$environment" deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment but with no tag is not allowed" {
    # Given
    environment='staging'
    expected_output='ERROR: You need to specify an existing tag to deploy'

    # When
    run pc -e "$environment" deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment with a malformed tag is not allowed" {
    # Given
    environment='staging'
    non_valid_tag='bats-tests'
    expected_output='tag format should be Semantic Versioning compliant x.x.x'

    # When
    run pc -e "$environment" -t "$non_valid_tag" deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment with local tag but not existing remotely is not allowed" {
    # Given
    index=0
    expected_output='ERROR: You need to specify an existing remote tag to deploy'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock}" "fetch" 3
    # git checkout master
    mock_set_output "${mock}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock}" "pull production" 13
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock}" "tagged_commit" 14
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock}" "" 15
    # exit_restoring_branch
    mock_set_output "${mock}" "checkout origin branch" 16

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e production -t 0.0.0 deploy-backend

    # Then
    echo "$(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 16 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment with valid tag but not deployed in staging is not allowed" {
    # Given
    index=0
    expected_output='ERROR: Can only deploy in production commits that are also deployed in staging'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock}" "fetch" 3
    # git checkout master
    mock_set_output "${mock}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock}" "pull production" 13
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock}" "tagged_commit" 14
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock}" "v0.0.0" 15
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock}" "ok" 16
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock}" "commit_hash_not_in_staging" 17
    # exit_restoring_branch
    mock_set_output "${mock}" "checkout origin branch" 18

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e production -t 0.0.0 deploy-backend

    # Then
    echo "$(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 18 ]]

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}


@test "Deploy-backend on production environment" {
    # Given
    index=0
    expected_output='/!\\ You just deployed to production. Was the version also delivered to integration ?'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock}" "fetch" 3
    # git checkout master
    mock_set_output "${mock}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock}" "pull production" 13
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock}" "tagged_commit" 14
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock}" "v0.0.0" 15
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock}" "ok" 16
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock}" "commit_hash" 17
    # git push -f origin HEAD:"$ENV"
    mock_set_output "${mock}" "Exit success !" 18

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e production -t 0.0.0 deploy-backend

    # Then
    echo "$(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 19 ]]

    for index in ${!lines[@]};
    do
        echo "Output $index: ${lines[index]}"
    done

    echo "Status: ""$status"
    [ "$status" -eq 0 ]

    index=$((index))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}