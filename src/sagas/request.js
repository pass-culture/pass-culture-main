import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, getToken, successData } from '../reducers/data'
import { apiData } from '../utils/api'

function * fromWatchRequestActions (action) {
  const { method, path, config } = action
  const body = config && config.body
  const type = config && config.type
  const token = yield type && select(state => state.data[`${type}Token`])
  try {
    const data = yield call(apiData, action.method, action.path, { body, token })
    yield put(successData(method, path, data, config))
  } catch (error) {
    console.warn(error)
    yield put(failData(method, path, error, config))
  }
}

export function * watchRequestActions () {
  yield takeEvery(({ type }) => /REQUEST_(.*)/.test(type), fromWatchRequestActions)
}
