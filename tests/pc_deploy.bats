#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock

debug_mock() {
  # Debug
  # Use the below line if you actually want to see all the arguments the function used to call the 'stub'
  index=1
  while [ $index -le $(mock_get_call_num ${mock}) ]
  do
    echo "# call_args: " $(mock_get_call_args ${mock} $index) >&3
    index=$((index+1))
  done
}




teardown() {
    # Cleanup our stub and fixup the PATH
    unlink "${mock_path}/${mocked_command}"
    PATH="${PATH/${mock_path}:/}"
}


create_mock_for_test_1() {
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
}

@test "1 - Deploy-backend on known environment with local tag but not existing remotely is not allowed" {
  # Given
  expected_output='ERROR: You need to specify an existing remote tag to deploy'
  mocked_command="git"

  create_mock_for_test_1

  # Test mock is set up properly
  [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

  # When
  run pc -e bats-tests -t 0.0.0 deploy-backend

  # Then
  echo "$(mock_get_call_num ${mock})"
  [[ "$(mock_get_call_num ${mock})" -eq 3 ]]

  echo "Status: ""$status"
  [ "$status" -eq 1 ]

  echo "Expected: ""$expected_output"
  echo "Output: ""${lines[0]}"
  [[ "${lines[0]}" =~ .*$expected_output.* ]]
}


create_mock_for_test_2() {
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
    # git checkout bats-tests
    mock_set_output "${mock}" "checkout bats-tests" 8
    # git pull origin bats-tests || exit_restoring_branch
    mock_set_output "${mock}" "pull bats-tests" 9
    # git checkout staging
    mock_set_output "${mock}" "checkout staging" 10
    # git pull origin staging || exit_restoring_branch
    mock_set_output "${mock}" "pull staging" 11
    # git checkout demo
    mock_set_output "${mock}" "checkout demo" 12
    # git pull origin demo || exit_restoring_branch
    mock_set_output "${mock}" "pull demo" 13
    # git checkout integration
    mock_set_output "${mock}" "checkout integration" 14
    # git pull origin integration || exit_restoring_branch
    mock_set_output "${mock}" "pull integration" 15
    # git checkout production
    mock_set_output "${mock}" "checkout production" 16
    # git pull origin production || exit_restoring_branch
    mock_set_output "${mock}" "pull production" 17
    # git tag -l --points-at "$commit_to_deploy" | wc -l
    mock_set_output "${mock}" "blabla" 18
    # git log -n 1 --pretty=format:%H staging
    mock_set_output "${mock}" "pretty log" 19
}


@test "2 - Deploy-backend on known environment with valid tag but not deployed in staging is not allowed" {
  # Given
  index=0
  expected_output='ERROR: Can only deploy in production commits that are also deployed in staging'
  mocked_command="git"

  create_mock_for_test_2

  # Test mock is set up properly
  [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

  # When
  run pc -e bats-tests -t 0.0.0 deploy-backend

  # Then
  echo "$(mock_get_call_num ${mock})"
  [[ "$(mock_get_call_num ${mock})" -eq 20 ]]

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
}


create_mock_for_test_3() {
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
  # git checkout bats-tests
  mock_set_output "${mock}" "checkout bats-tests" 8
  # git pull origin bats-tests || exit_restoring_branch
  mock_set_output "${mock}" "pull bats-tests" 9
  # git checkout staging
  mock_set_output "${mock}" "checkout staging" 10
  # git pull origin staging || exit_restoring_branch
  mock_set_output "${mock}" "pull staging" 11
  # git checkout demo
  mock_set_output "${mock}" "checkout demo" 12
  # git pull origin demo || exit_restoring_branch
  mock_set_output "${mock}" "pull demo" 13
  # git checkout integration
  mock_set_output "${mock}" "checkout integration" 14
  # git pull origin integration || exit_restoring_branch
  mock_set_output "${mock}" "pull integration" 15
  # git checkout production
  mock_set_output "${mock}" "checkout production" 16
  # git pull origin production || exit_restoring_branch
  mock_set_output "${mock}" "pull production" 17
  # git tag -l --points-at "$commit_to_deploy" | wc -l
  mock_set_output "${mock}" "commit_hash" 18
  # git log -n 1 --pretty=format:%H staging
  mock_set_output "${mock}" "commit_hash" 19
  # git checkout "$ENV"
  mock_set_output "${mock}" "checkout ENV" 20
  # git merge "$commit_to_deploy"
  mock_set_output "${mock}" "merge" 21
  # git push origin "$ENV"
  mock_set_output "${mock}" "push ENV" 22
}

@test "3 - Deploy-backend on production environment" {
  # Given
  index=0
  expected_output='/!\\ You just deployed to production. Was the version also delivered to integration ?'
  mocked_command="git"

  create_mock_for_test_3

  # Test mock is set up properly
  [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

  # When
  run pc -e bats-tests -t 0.0.0 deploy-backend

  # Then
  echo "$(mock_get_call_num ${mock})"
  [[ "$(mock_get_call_num ${mock})" -eq 23 ]]

  for index in ${!lines[@]};
  do
    echo "Output $index: ${lines[index]}"
  done

  echo "Status: ""$status"
  [ "$status" -eq 1 ]

  echo "Expected: ""$expected_output"
  echo "Output: ${lines[index]}"
  [[ "${lines[index]}" =~ .*$expected_output.* ]]
}