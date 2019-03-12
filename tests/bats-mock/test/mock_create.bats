#!/usr/bin/env bats

load ../src/bats-mock

teardown() {
  rm "${BATS_TMPDIR}/bats-mock.$$."*
}

@test 'mock_create creates a program' {
  run mock_create
  [[ "${status}" -eq 0 ]]
  [[ -x "${output}" ]]
}

@test 'mock_create names the program uniquely' {
  run mock_create
  [[ "${status}" -eq 0 ]]
  mock="${output}"
  run mock_create
  [[ "${status}" -eq 0 ]]
  [[ "${output}" != "${mock}" ]]
}

@test 'mock_create creates a program in BATS_TMPDIR' {
  run mock_create
  [[ "${status}" -eq 0 ]]
  [[ "$(dirname ${output})" = "${BATS_TMPDIR}" ]]
}
