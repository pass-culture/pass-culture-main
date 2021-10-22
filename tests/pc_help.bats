#!./test/libs/bats/bin/bats


@test "PC script should show its usage when pc -h" {
  # Given
  expected_output="pc [-h] [-e env -b backend -f file c] -- program to deal with Pass Culture ecosystem"

  # When
  run pc -h

  # Then

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "$expected_output" ]
}
