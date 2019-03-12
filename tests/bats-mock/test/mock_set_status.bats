#!/usr/bin/env bats

load mock_test_suite

@test 'mock_set_status requires mock to be specified' {
  run mock_set_status
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_set_status requires status to be specified' {
  run mock_set_status "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Status must be specified' ]]
}

@test 'mock_set_status 0 status is set by default' {
  run "${mock}"
  [[ "${status}" -eq 0 ]]
}

@test 'mock_set_status sets a status' {
  mock_set_status "${mock}" 127
  run "${mock}"
  [[ "${status}" -eq 127 ]]
}

@test 'mock_set_status sets an n-th status' {
  mock_set_status "${mock}" 127 2
  mock_set_status "${mock}" 255 4
  run "${mock}"
  [[ "${status}" -eq 0 ]]
  run "${mock}"
  [[ "${status}" -eq 127 ]]
  run "${mock}"
  [[ "${status}" -eq 0 ]]
  run "${mock}"
  [[ "${status}" -eq 255 ]]
  run "${mock}"
  [[ "${status}" -eq 0 ]]
}
