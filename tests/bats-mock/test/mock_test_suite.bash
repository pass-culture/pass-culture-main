#!/usr/bin/env bash

load ../src/bats-mock

setup() {
  mock="$(mock_create)"
}

teardown() {
  rm "${mock}"*
}
