#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock

debug_mock() {
    # Use the below line if you actually want to see all the arguments the function used to call the 'stub'
    index=1
    while [ $index -le $(mock_get_call_num ${mock}) ]
    do
        echo "# call_args: " $(mock_get_call_args ${mock} $index) >&3
        index=$((index+1))
    done
}


@test "1 - Deploy-frontend-pro on known environment with local tag but not existing remotely is not allowed" {
    # Given
    expected_output='ERROR: You need to specify an existing remote tag to deploy'

    mocked_command="git"
    mock="$(mock_create)"
    mock_path="${mock%/*}"
    mock_file="${mock##*/}"
    ln -sf "${mock_path}/${mock_file}" "${mock_path}/${mocked_command}"
    PATH="${mock_path}:$PATH"

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock}" "bats-tests" 1
    # call with param: ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock}" "" 2
    # call with param: checkout bats-tests (function exit_restoring_branch)
    mock_set_output "${mock}" "ok" 3

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e bats-tests -t 0.0.0 deploy-frontend-pro

    # Then
    echo "$(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 3 ]]

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path}/${mocked_command}"
    PATH="${PATH/${mock_path}:/}"
}

create_mock_for_test_2() {
    mocked_command="git"

    mock="$(mock_create)"
    mock_path="${mock%/*}"
    mock_file="${mock##*/}"
    ln -sf "${mock_path}/${mock_file}" "${mock_path}/${mocked_command}"
    PATH="${mock_path}:$PATH"

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock}" "bats-tests" 1
    # call with param: ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock}" "v0.0.0" 2
    # call with param: checkout bats-tests (function exit_restoring_branch)
    mock_set_output "${mock}" "exit_restoring_branch" 3
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock}" "commit_hash" 4
    # git fetch
    mock_set_output "${mock}" "fetch" 5
    # git checkout master
    mock_set_output "${mock}" "checkout master" 6
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock}" "pull master" 7
    # git checkout staging
    mock_set_output "${mock}" "checkout staging" 8
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock}" "pull staging" 9
    # git checkout demo
    mock_set_output "${mock}" "checkout demo" 10
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock}" "pull demo" 11
    # git checkout integration
    mock_set_output "${mock}" "checkout integration" 12
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock}" "pull integration" 13
    # git checkout production
    mock_set_output "${mock}" "checkout production" 14
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock}" "pull production" 15
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock}" "blabla" 16
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock}" "pretty log" 17
}


@test "2 - Deploy-frontend-pro on known environment with valid tag but not deployed in staging is not allowed" {
    # Given
    index=0
    expected_output='ERROR: Can only deploy in production commits that are also deployed in staging'

    create_mock_for_test_2

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e bats-tests -t 0.0.0 deploy-frontend-pro

    # Then
    echo "$(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 18 ]]

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path}/${mocked_command}"
    PATH="${PATH/${mock_path}:/}"
}



@test "3 - Deploy-frontend-pro on staging environment" {
    # Given
    index=0
    expected_output="Exit success !"

    mocked_command_1="git"
    mocked_command_2="netlify"

    mock_1="$(mock_create)"
    mock_2="$(mock_create)"
    mock_path_1="${mock_1%/*}"
    mock_path_2="${mock_2%/*}"
    mock_file_1="${mock_1##*/}"
    mock_file_2="${mock_2##*/}"
    ln -sf "${mock_path_1}/${mock_file_1}" "${mock_path_1}/${mocked_command_1}"
    ln -sf "${mock_path_2}/${mock_file_2}" "${mock_path_2}/${mocked_command_2}"
    PATH="${mock_path_1}:$PATH"
    PATH="${mock_path_2}:$PATH"

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_1}" "bats-tests" 1
    # call with param: ls-remote --tags origin refs/tags/v0.0.0
    mock_set_output "${mock_1}" "v0.0.0" 2
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock_1}" "commit_hash" 3
    # git fetch
    mock_set_output "${mock_1}" "fetch" 4
    # git checkout master
    mock_set_output "${mock_1}" "checkout master" 5
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock_1}" "pull master" 6
    # git checkout staging
    mock_set_output "${mock_1}" "checkout staging" 7
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock_1}" "pull staging" 8
    # git checkout demo
    mock_set_output "${mock_1}" "checkout demo" 9
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock_1}" "pull demo" 10
    # git checkout integration
    mock_set_output "${mock_1}" "checkout integration" 11
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock_1}" "pull integration" 12
    # git checkout production
    mock_set_output "${mock_1}" "checkout production" 13
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock_1}" "pull production" 14
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock_1}" "commit_hash" 15
    # git checkout "$ENV"
    mock_set_output "${mock_1}" "checkout ENV" 16
    # git merge "$commit_to_deploy"
    mock_set_output "${mock_1}" "merge" 17
    # git push origin "$ENV"
    mock_set_output "${mock_1}" "push ENV" 18
    # exit success restoring branch
    mock_set_output "${mock_1}" "Exit success !" 19
    mock_set_output "${mock_1}" "Exit success !" 20

    # Mock Netlify
    mock_set_output "${mock_2}" "Netlify deploy" 1

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_1})" ]]
    [[ "$(readlink -e $(which netlify))" == "$(readlink -e ${mock_2})" ]]

    # When
    run pc -e staging -t 0.0.0 deploy-frontend-pro

    # Then
    echo "$(mock_get_call_num ${mock_1})"
    echo "$(mock_get_call_num ${mock_2})"
    [[ "$(mock_get_call_num ${mock_1})" -eq 20 ]]

    for index in ${!lines[@]};
    do
    echo "Output $index: ${lines[index]}"
    done

    echo "Status: ""$status"
    [ "$status" -eq 0 ]

    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]


    [[ "$(mock_get_call_num ${mock_2})" -eq 1 ]]

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_1}/${mocked_command_1}"
    PATH="${PATH/${mock_path_1}:/}"

    unlink "${mock_path_2}/${mocked_command_2}"
    PATH="${PATH/${mock_path_2}:/}"
}