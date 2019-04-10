#!./test/libs/bats/bin/bats

load bats-mock/src/bats-mock

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

@test "Deploy should not be run if current ENV is development" {
    # Given
    expected_output='Deploy backend cannot be run on the local environment. Use (for example) "pc -e staging -t X.Y.Z deploy".'

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
    expected_output='Can only deploy-backend in staging, demo, integration and production'

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

@test "Deploy on known environment with a malformed tag is not allowed" {
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
    expected_output='ERROR: You need to deploy only tagged version'

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
    # git ls-remote --tags origin refs/tags/v"$TAG_NAME"
    mock_set_output "${mock}" "" 14
    # exit_restoring_branch
    mock_set_output "${mock}" "checkout origin branch" 15

    echo "Before test mock is set up"

    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock})" ]]

    # When
    run pc -e staging -t 0.0.0 deploy

    # Then
    debug_mock
    echo "Number of calls: $(mock_get_call_num ${mock})"
    [[ "$(mock_get_call_num ${mock})" -eq 15 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}
