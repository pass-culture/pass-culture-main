import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, successData } from '../reducers/data'
import { apiData } from '../utils/api'

function * fromWatchRequestDataActions (action) {
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

export function * watchDataActions () {
  yield takeEvery(({ type }) => /REQUEST_DATA_(.*)/.test(type), fromWatchRequestDataActions)
}
