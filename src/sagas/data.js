import { call, put, select, takeEvery } from 'redux-saga/effects'

import { assignData, failData, successData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { apiData } from '../utils/api'

function * fromWatchRequestDataActions (action) {
  const { method, path, config } = action
  const body = config && config.body
  const type = config && config.type
  const token = yield type && select(state => state.data[`${type}Token`])
  try {
    const result = yield call(apiData, action.method, action.path, { body, token })
    if (result.data) {
      yield put(successData(method, path, result.data, config))
    } else {
      console.warn(result.error)
      yield put(failData(method, path, result.error, config))
    }
  } catch (error) {
    console.warn('error', error)
    yield put(failData(method, path, error, config))
  }
}

function * fromWatchFailDataActions (action) {
  yield put(assignData({ error: action.error }))
}

function * fromWatchSuccessDataActions (action) {
  yield put(resetForm())
}

export function * watchDataActions () {
  yield takeEvery(({ type }) => /REQUEST_DATA_(.*)/.test(type), fromWatchRequestDataActions)
  yield takeEvery(({ type }) => /FAIL_DATA_(.*)/.test(type), fromWatchFailDataActions)
  yield takeEvery(({ type }) => /SUCCESS_DATA_(POST|PUT)_(.*)/.test(type), fromWatchSuccessDataActions)
}
