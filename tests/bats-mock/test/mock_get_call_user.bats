#!/usr/bin/env bats

load mock_test_suite

@test 'mock_get_call_user requires mock to be specified' {
  run mock_get_call_user
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_get_call_user requires the mock to be called' {
  run mock_get_call_user "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_user outputs the last call user if no n is specified' {
  _USER='alice' "${mock}"
  _USER='bob' "${mock}"
  run mock_get_call_user "${mock}"
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'bob' ]]
}

@test 'mock_get_call_user requires the mock to be called 1 time' {
  run mock_get_call_user "${mock}" 1
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_user requires the mock to be called 2 times' {
  "${mock}"
  run mock_get_call_user "${mock}" 1
  [[ "${status}" -eq 0 ]]
  run mock_get_call_user "${mock}" 2
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 2 time(s)' ]]
}

@test 'mock_get_call_user requires the mock to be called 3 times' {
  run mock_get_call_user "${mock}" 3
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 3 time(s)' ]]
}

@test 'mock_get_call_user outputs the n-th call user' {
  _USER='alice' "${mock}"
  _USER='bob' "${mock}"
  _USER='charlot' "${mock}"
  _USER='dan' "${mock}"
  _USER='eve' "${mock}"
  run mock_get_call_user "${mock}" 2
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'bob' ]]
  run mock_get_call_user "${mock}" 4
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'dan' ]]
}
