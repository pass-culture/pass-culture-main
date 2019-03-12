#!/usr/bin/env bats

load mock_test_suite

@test 'mock_set_side_effect requires mock to be specified' {
  run mock_set_side_effect
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Mock must be specified' ]]
}

@test 'mock_set_side_effect requires side_effect to be specified' {
  run mock_set_side_effect "${mock}"
  [[ "${status}" -eq 1 ]]
  [[ "${output}" =~ 'Side effect must be specified' ]]
}

@test 'mock_set_side_effect sets a side_effect 1' {
  mock_set_side_effect "${mock}" "touch ${mock}.side_effect_1"
  run "${mock}"
  [[ -e "${mock}.side_effect_1" ]]
}

@test 'mock_set_side_effect sets a side_effect 2' {
  mock_set_side_effect "${mock}" "touch ${mock}.side_effect_2"
  run "${mock}"
  [[ -e "${mock}.side_effect_2" ]]
}

@test 'mock_set_side_effect sets an side_effect from STDIN if - is specified' {
  mock_set_side_effect "${mock}" - <<< "touch ${mock}.stdin_side_effect_1"
  run "${mock}"
  [[ -e "${mock}.stdin_side_effect_1" ]]
}

@test 'mock_set_side_effect sets a multiline side_effect' {
  mock_set_side_effect "${mock}" "touch ${mock}.side_effect_3\ntouch ${mock}.side_effect_4"
  run "${mock}"
  [[ -e "${mock}.side_effect_3" ]]
  [[ -e "${mock}.side_effect_4" ]]
}

@test 'mock_set_side_effect sets an n-th side_effect' {
  mock_set_side_effect "${mock}" "touch ${mock}.side_effect_5" 2
  mock_set_side_effect "${mock}" "touch ${mock}.side_effect_6" 4
  run "${mock}"
  [[ ! -e "${mock}.side_effect_5" && ! -e "${mock}.side_effect_6" ]]
  run "${mock}"
  [[ -e "${mock}.side_effect_5" && ! -e "${mock}.side_effect_6" ]]
  run "${mock}"
  [[ -e "${mock}.side_effect_5" && ! -e "${mock}.side_effect_6" ]]
  run "${mock}"
  [[ -e "${mock}.side_effect_5" && -e "${mock}.side_effect_6" ]]
}
