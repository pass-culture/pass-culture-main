import { call, takeEvery, put } from 'redux-saga/effects'

import { successGetProducts } from '../reducers/request'
import api from '../utils/api'

function * fromWatchRequestActions (action) {
  const data = yield call(api, 'products')
  yield put(successGetProducts(data))
}

export function * watchRequestActions () {
  yield takeEvery(({ type }) => /REQUEST_(.*)/.test(type), fromWatchRequestActions)
}
