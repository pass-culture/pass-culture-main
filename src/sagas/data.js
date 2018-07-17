import { call, put, select, takeEvery } from 'redux-saga/effects'

import { assignData, failData, successData } from '../reducers/data'
import { fetchData, localData } from '../utils/request'

function * fromWatchRequestDataActions(action) {
  // UNPACK
  const { method, path, config } = action
  const body = config && config.body
  const hook = config && config.hook
  const local = config && config.local
  const type = config && config.type
  // TOKEN
  const token = yield type && select(state => state.data[`${type}Token`])
  // DATA
  try {
    const dataMethod = local ? localData : fetchData
    const result = yield call(dataMethod, method, path, { body, token })
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
    yield put(failData(method, path, { global: [error.toString()] }, config))
  }
}

function * fromWatchFailDataActions(action) {
  const errors = yield select(state => state.data.errors)
  yield put(assignData({ errors: Object.assign({}, errors, action.errors) }))
}

function * fromWatchSuccessDataActions(action) {
  const { config, method, path } = action
  const local = config && config.local
  if (method !== 'GET' && !local) {
    // FROM A MUTATING FETCH REQUEST
    // WE MAKE SURE HERE TO UPDATE ALSO THE DEXIE
    yield call(localData, method, path, { body: action.data })
  }
}

export function * watchDataActions() {
  yield takeEvery(
    ({ type }) => /REQUEST_DATA_(.*)/.test(type),
    fromWatchRequestDataActions
  )
  yield takeEvery(
    ({ type }) => /FAIL_DATA_(.*)/.test(type),
    fromWatchFailDataActions
  )
  yield takeEvery(
    ({ type }) => /SUCCESS_DATA_(.*)/.test(type),
    fromWatchSuccessDataActions
  )
}
