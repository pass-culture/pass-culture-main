import { call, put, select, takeEvery } from 'redux-saga/effects'

import { assignData, failData, successData } from '../reducers/data'
import { resetForm } from '../reducers/form'
import { setGeolocationPosition } from '../reducers/geolocation'
import { bulkData } from '../utils/dexie'
import { fetchData, syncData } from '../utils/request'
import { getGeolocationPosition } from '../utils/geolocation'

function * fromWatchRequestDataActions (action) {
  // UNPACK
  const { method, path, config } = action
  const body = config && config.body
  const hook = config && config.hook
  const sync = config && config.sync
  const type = config && config.type
  // GEOLOCATION
  const position = yield config && config.isGeolocated &&
    call(getGeolocationPosition, { highAccuracy: true })
  yield put(setGeolocationPosition(position))
  // TOKEN
  const token = yield type && select(state => state.data[`${type}Token`])
  // DATA
  try {
    const dataMethod = method === 'GET'
      ? (sync && syncData) || fetchData
      : fetchData
    const result = yield call(dataMethod,
      method,
      path,
      { body, position, token }
    )
    console.log(path, 'result', result)
    if (hook) {
      yield call(hook, method, path, result, config)
    }
    if (result.data) {
      if (sync && (method === 'POST' || method === 'PUT')) {
        yield call(bulkData, method, path, result.data, config)
      }
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
