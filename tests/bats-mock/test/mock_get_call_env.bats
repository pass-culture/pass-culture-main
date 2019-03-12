#!/usr/bin/env bats

load mock_test_suite

@test 'mock_get_call_env requires mock to be specified' {
  run mock_get_call_env
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_get_call_env requires variable to be specified' {
  run mock_get_call_env "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Variable name must be specified' ]]
}

@test 'mock_get_call_env requires the mock to be called' {
  run mock_get_call_env "${mock}" 'VAR'
  echo "${output}" >&2
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_env outputs the last call variable if no n is specified' {
  VAR='value 1' "${mock}"
  VAR='value 2' "${mock}"
  run mock_get_call_env "${mock}" 'VAR'
  echo "${output}" >&2
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'value 2' ]]
}

@test 'mock_get_call_env requires the mock to be called 1 time' {
  run mock_get_call_env "${mock}" 'VAR' 1
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 1 time(s)' ]]
}

@test 'mock_get_call_env requires the mock to be called 2 times' {
  "${mock}"
  run mock_get_call_env "${mock}" 'VAR' 1
  [[ "${status}" -eq 0 ]]
  run mock_get_call_env "${mock}" 'VAR' 2
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 2 time(s)' ]]
}

@test 'mock_get_call_env requires the mock to be called 3 times' {
  run mock_get_call_env "${mock}" 'VAR' 3
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be called at least 3 time(s)' ]]
}

@test 'mock_get_call_env outputs the n-th call variable' {
  VAR='value 3' "${mock}"
  VAR='value 4' "${mock}"
  VAR='value 5' "${mock}"
  VAR='value 6' "${mock}"
  VAR='value 7' "${mock}"
  run mock_get_call_env "${mock}" 'VAR' 2
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'value 4' ]]
  run mock_get_call_env "${mock}" 'VAR' 4
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'value 6' ]]
}

@test 'mock_get_call_env process multiple variables' {
  VAR1='value 8' VAR2='value 9' "${mock}"
  run mock_get_call_env "${mock}" 'VAR1'
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'value 8' ]]
  run mock_get_call_env "${mock}" 'VAR2'
  [[ "${status}" -eq 0 ]]
  [[ "${output}" = 'value 9' ]]
}

@test 'mock_get_call_env returns nothing if variable is not set' {
  "${mock}"
  run mock_get_call_env "${mock}" 'NOTSET'
  [[ "${status}" -eq 0 ]]
  [[ -z "${output}" ]]
}
