#!/usr/bin/env bats

load mock_test_suite

@test 'mock_get_call_args requires mock to be specified' {
  run mock_get_call_args
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_get_call_args requires the mock to be called' {
  run mock_get_call_args "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_args outputs the last call args if no n is specified' {
  "${mock}" one
  "${mock}" two
  run mock_get_call_args "${mock}"
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'two' ]]
}

@test 'mock_get_call_args requires the mock to be called 1 time' {
  run mock_get_call_args "${mock}" 1
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_args requires the mock to be called 2 times' {
  "${mock}"
  run mock_get_call_args "${mock}" 1
  [[ "${status}" -eq 0 ]]
  run mock_get_call_args "${mock}" 2
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 2 time(s)' ]]
}

@test 'mock_get_call_args requires the mock to be called 3 times' {
  run mock_get_call_args "${mock}" 3
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 3 time(s)' ]]
}

@test 'mock_get_call_args outputs the n-th call args' {
  "${mock}" three
  "${mock}" four
  "${mock}" five
  "${mock}" six
  "${mock}" seven
  run mock_get_call_args "${mock}" 2
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'four' ]]
  run mock_get_call_args "${mock}" 4
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'six' ]]
}
