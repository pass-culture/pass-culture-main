import { call, put, select, takeEvery } from 'redux-saga/effects'

import { successData } from '../reducers/request'
import { apiData } from '../utils/api'

function * fromWatchRequestActions (action) {
  const { method, path, config } = action
  const token = yield select(({ request: { token } }) => token)
  const data = yield call(apiData, action.path, { token })
  yield put(successData(method, path, data, config))
}

export function * watchRequestActions () {
  yield takeEvery(({ type }) => /REQUEST_(.*)/.test(type), fromWatchRequestActions)
}
