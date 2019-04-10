#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock

debug_mock() {
    # Use the below line if you actually want to see all the arguments the function used to call the 'stub'
    index=1
    while [ $index -le $(mock_get_call_num ${mock_git}) ]
    do
        echo "# call_args: " $(mock_get_call_args ${mock_git} $index) >&3
        index=$((index+1))
    done
}

mocked_command_git=""
mock_git=""
mock_path_git=""
mock_file_git=""

mocked_command_netlify=""
mock_netlify=""
mock_path_netlify=""
mock_file_netlify=""


setup(){
    mocked_command_git="git"
    mock_git="$(mock_create)"
    mock_path_git="${mock_git%/*}"
    mock_file_git="${mock_git##*/}"
    ln -sf "${mock_path_git}/${mock_file_git}" "${mock_path_git}/${mocked_command_git}"
    PATH="${mock_path_git}:$PATH"
    
    mocked_command_netlify="netlify"
    mock_netlify="$(mock_create)"
    mock_path_netlify="${mock_netlify%/*}"
    mock_file_netlify="${mock_netlify##*/}"
    ln -sf "${mock_path_netlify}/${mock_file_netlify}" "${mock_path_netlify}/${mocked_command_netlify}"
    PATH="${mock_path_netlify}:$PATH"
}

teardown(){
    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_git}/${mocked_command_git}"
    PATH="${PATH/${mock_path_git}:/}"
    
    unlink "${mock_path_netlify}/${mocked_command_netlify}"
    PATH="${PATH/${mock_path_netlify}:/}"
}


@test "Deploy-frontend-pro on known environment with local tag but not existing remotely is not allowed" {
    # Given
    expected_output='ERROR: You need to specify an existing remote tag to deploy'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock_git}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock_git}" "fetch" 3
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock_git}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock_git}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock_git}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock_git}" "tagged_commit" 13
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock_git}" "" 14
    # exit_restoring_branch
    mock_set_output "${mock_git}" "checkout origin branch" 15

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]

    # When
    run pc -e staging -t 0.0.0 deploy-frontend-pro

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 15 ]]

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


@test "Deploy-frontend-pro on known environment with valid tag but not deployed in staging is not allowed" {
    # Given
    index=0
    expected_output='ERROR: Can only deploy in production commits that are also deployed in staging'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock_git}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock_git}" "fetch" 3
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock_git}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock_git}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock_git}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock_git}" "v0.0.0" 14
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock_git}" "ok" 15
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock_git}" "commit_hash_not_in_staging" 16
    # exit_restoring_branch
    mock_set_output "${mock_git}" "checkout origin branch" 17

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]
    [[ "$(readlink -e $(which netlify))" == "$(readlink -e ${mock_netlify})" ]]

    # When
    run pc -e production -t 0.0.0 deploy-frontend-pro

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 17 ]]

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



@test "Deploy-frontend-pro on production environment" {
    # Given
    index=0
    expected_output='/!\\ You just deployed to production. Was the version also delivered to integration ?'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # $(git log -n 1 --pretty=format:%H)
    mock_set_output "${mock_git}" "commit_hash" 2
    # git fetch
    mock_set_output "${mock_git}" "fetch" 3
    # git checkout master
    mock_set_output "${mock_git}" "checkout master" 4
    # git pull origin master || exit_restoring_branch
    mock_set_output "${mock_git}" "pull master" 5
    # git checkout staging
    mock_set_output "${mock_git}" "checkout staging" 6
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock_git}" "pull staging" 7
    # git checkout demo
    mock_set_output "${mock_git}" "checkout demo" 8
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock_git}" "pull demo" 9
    # git checkout integration
    mock_set_output "${mock_git}" "checkout integration" 10
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock_git}" "pull integration" 11
    # git checkout production
    mock_set_output "${mock_git}" "checkout production" 12
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock_git}" "pull production" 13
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock_git}" "v0.0.0" 14
    # git checkout "v$TAG_NAME"
    mock_set_output "${mock_git}" "ok" 15
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock_git}" "commit_hash" 16
    # git push -f origin HEAD:"$ENV"
    mock_set_output "${mock_git}" "psuh force origin HEAD:ENV" 17
    # git checkout bats-tests
    mock_set_output "${mock_git}" "Exit success !" 18

    # Mock Netlify
    mock_set_output "${mock_netlify}" "Netlify deploy" 1

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]
    [[ "$(readlink -e $(which netlify))" == "$(readlink -e ${mock_netlify})" ]]

    # When
    run pc -e production -t 0.0.0 deploy-frontend-pro

    # Then
    echo "Number of calls (git): $(mock_get_call_num ${mock_git})"
    echo "Number of calls (netlify) : $(mock_get_call_num ${mock_netlify})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 18 ]]
    [[ "$(mock_get_call_num ${mock_netlify})" -eq 1 ]]

    echo "Status: ""$status"
    [ "$status" -eq 0 ]

    for index in ${!lines[@]};
    do
        echo "Output $index: ${lines[index]}"
    done
    index=$((index))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}
