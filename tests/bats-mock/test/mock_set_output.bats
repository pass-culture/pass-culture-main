#!/usr/bin/env bats

load mock_test_suite

@test 'mock_set_output requires mock to be specified' {
  run mock_set_output
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_set_output requires output to be specified' {
  run mock_set_output "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Output must be specified' ]]
}

@test 'mock_set_output no output is set by default' {
  run "${mock}"
  [[ -z "${output}" ]]
}

@test 'mock_set_output sets an output 1' {
  mock_set_output "${mock}" 'output 1'
  run "${mock}"
  [[ "${output}" = 'output 1' ]]
}

@test 'mock_set_output sets an output 2' {
  mock_set_output "${mock}" 'output 2'
  run "${mock}"
  [[ "${output}" = 'output 2' ]]
}

@test 'mock_set_output sets an output from STDIN if - is specified' {
  mock_set_output "${mock}" - <<< 'stdin output 1'
  run "${mock}"
  [[ "${output}" = 'stdin output 1' ]]
}

@test 'mock_set_output sets a multiline output' {
  mock_set_output "${mock}" "output 3\noutput 4"
  run "${mock}"
  [[ "${lines[0]}" = 'output 3' ]]
  [[ "${lines[1]}" = 'output 4' ]]
}

@test 'mock_set_output sets an n-th output' {
  mock_set_output "${mock}" 'output 5' 2
  mock_set_output "${mock}" 'output 6' 4
  run "${mock}"
  [[ -z "${output}" ]]
  run "${mock}"
  [[ "${output}" = 'output 5' ]]
  run "${mock}"
  [[ -z "${output}" ]]
  run "${mock}"
  [[ "${output}" = 'output 6' ]]
  run "${mock}"
  [[ -z "${output}" ]]
}
