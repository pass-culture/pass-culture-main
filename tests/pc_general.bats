#!./test/libs/bats/bin/bats


@test "Should show its usage when pc -h" {
  # Given
  input=""
  expected_output="pc [-h] [-e env -b backend c] -- program to deal with Pass Culture ecosystem"

  # When
  run pc -h

  # Then
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "$expected_output" ]
}



@test "Deploy-backend should not be run if current $ENV is development" {
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
    expected_output='Can only deploy-backend in staging, demo, integration and production'

    # When
    run pc -e unexisting-env deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment but with no tag is not allowed" {
    # Given
    environment=staging
    expected_output='ERROR: You need to specify an existing tag to deploy'

    # When
    run pc -e $environment deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}

@test "Deploy-backend on known environment with a malformed tag is not allowed" {
    # Given
    environment=staging
    non_valid_tag='bats-tests'
    expected_output='tag format should be Semantic Versioning compliant x.x.x'

    # When
    run pc -e $environment -t "$non_valid_tag" deploy-backend

    # Then

    echo "Status: ""$status"
    [ "$status" -eq 1 ]

    echo "Expected: ""$expected_output"
    echo "Output: ""${lines[0]}"
    [[ "${lines[0]}" =~ .*$expected_output.* ]]
}



