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
}

mocked_command_git=""
mock_git=""
mock_path_git=""
mock_file_git=""

mocked_command_yarn=""
mock_yarn=""
mock_path_yarn=""
mock_file_yarn=""

setup(){
    mocked_command_git="git"
    mock_git="$(mock_create)"
    mock_path_git="${mock_git%/*}"
    mock_file_git="${mock_git##*/}"
    ln -sf "${mock_path_git}/${mock_file_git}" "${mock_path_git}/${mocked_command_git}"
    PATH="${mock_path_git}:$PATH"

    mocked_command_yarn="yarn"
    mock_yarn="$(mock_create)"
    mock_path_yarn="${mock_yarn%/*}"
    mock_file_yarn="${mock_yarn##*/}"
    ln -sf "${mock_path_yarn}/${mock_file_yarn}" "${mock_path_yarn}/${mocked_command_yarn}"
    PATH="${mock_path_yarn}:$PATH"
}

teardown(){
    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_git}/${mocked_command_git}"
    PATH="${PATH/${mock_path_git}:/}"

    # Cleanup our stub and fixup the PATH
    unlink "${mock_path_yarn}/${mocked_command_yarn}"
    PATH="${PATH/${mock_path_yarn}:/}"
}


@test "Tag on known environment with a malformed tag is not allowed" {
    # Given
    non_valid_tag='bats-tests'
    expected_output='tag format should be Semantic Versioning compliant x.x.x'

    # When
    run pc -t "$non_valid_tag" tag

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Tag command tag main repo" {
    # Given
    index=0
    expected_output='New version tagged : 0.0.0'

    # call with param: symbolic-ref -q HEAD
    mock_set_output "${mock_git}" "bats-tests" 1
    # Mock to prevent git status --untracked-files=no --porcelain from making the script fail
    mock_set_output "${mock_git}" "" 2
    # git add version.txt
    mock_set_output "${mock_git}" "add version.txt" 3
    # git add pro package.json
    mock_set_output "${mock_git}" "add package.json" 4
    # git add adage-front package.json
    mock_set_output "${mock_git}" "add package.json" 5
    # call with param: git commit -m "🚀 $TAG_VERSION"
    mock_set_output "${mock_git}" "git commit -m 🚀 TAG_VERSION" 6
    # call with param: git tag "$TAG_VERSION"
    mock_set_output "${mock_git}" "tag-version main" 7
    # call with param: git push origin "$TAG_VERSION"
    mock_set_output "${mock_git}" "push tag main" 8
    # call with param: git checkout -b "maint/v$TAG_ITERATION"
    mock_set_output "${mock_git}" "git checkout -b "maint/v$TAG_ITERATION"" 9
    # call with param: git push origin "maint/v$TAG_ITERATION"
    mock_set_output "${mock_git}" "git push origin "maint/v$TAG_ITERATION"" 10
    # call with param: git reset --hard HEAD~1
    mock_set_output "${mock_git}" "git reset --hard HEAD~1" 11
    # call with param: git checkout "$current_branch"
    mock_set_output "${mock_git}" "git checkout current-branch" 12

    # Mock yarn
    # call with param: yarn version --new-version "$TAG_NAME"
    mock_set_output "${mock_yarn}" "yarn new-version pro" 1
    # call with param: yarn version --new-version "$TAG_NAME"
    mock_set_output "${mock_yarn}" "yarn new-version adage-front" 2


    # Test mock is set up properly
    [[ "$(readlink -e $(which git))" == "$(readlink -e ${mock_git})" ]]
    [[ "$(readlink -e $(which yarn))" == "$(readlink -e ${mock_yarn})" ]]

    # When
    run pc -t 0.0.0 tag

    # Then
    echo "Number of calls: $(mock_get_call_num ${mock_git})"
    echo "Number of calls: $(mock_get_call_num ${mock_yarn})"
    [[ "$(mock_get_call_num ${mock_git})" -eq 12 ]]
    [[ "$(mock_get_call_num ${mock_yarn})" -eq 2 ]]

    # Allow to follow last steps
    for index in ${!lines[@]}; do
      echo "Output $index: ${lines[index]}"
    done
    index=$((index-1))
    echo "Expected: ""$expected_output"
    echo "Output: ${lines[index]}"
    [[ "${lines[index]}" =~ .*$expected_output.* ]]
}
