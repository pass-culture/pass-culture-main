import { put, takeEvery } from 'redux-saga/effects'

import { mergeErrors } from '../reducers/errors'

export function* fromWatchFailDataActionsMergeErrors(action) {
  const {
    config: { apiPath, name },
    payload: { errors },
  } = action
  const errorsName = name || apiPath

  let patch
  if (Array.isArray(errors)) {
    patch = {}
    errors.forEach(error => Object.assign(patch, error))
  } else {
    patch = errors
  }

  yield put(mergeErrors(errorsName, patch))
}

export function* watchErrorsActions() {
  yield takeEvery(
    ({ type }) => /FAIL_DATA_(.*)/.test(type),
    fromWatchFailDataActionsMergeErrors
  )
}
