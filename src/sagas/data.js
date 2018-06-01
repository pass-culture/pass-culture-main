import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, successData } from '../reducers/data'
import { assignErrors } from '../reducers/errors'
import { fetchData } from '../utils/request'

function* fromWatchRequestDataActions(action) {
  // UNPACK
  const { method, path, config } = action
  const body = config && config.body
  const hook = config && config.hook
  const type = config && config.type
  // TOKEN
  const token = yield type && select(state => state.data[`${type}Token`])
  // DATA
  try {
    const result = yield call(fetchData, method, path, { body, token })
    if (hook) {
      yield call(hook, method, path, result, config)
    }
    if (result.data) {
      yield put(successData(method, path, result.data, config))
    } else {
      console.warn(result.errors)
      yield put(failData(method, path, result.errors, config))
    }
  } catch (error) {
    console.warn('error', error)
    yield put(failData(method, path, [{ global: error }], config))
  }
}

function* fromWatchFailDataActions(action) {

  yield put(assignErrors(action.errors))
}

export function* watchDataActions() {
  yield takeEvery(
    ({ type }) => /REQUEST_DATA_(.*)/.test(type),
    fromWatchRequestDataActions
  )
  yield takeEvery(
    ({ type }) => /FAIL_DATA_(.*)/.test(type),
    fromWatchFailDataActions
  )
}
