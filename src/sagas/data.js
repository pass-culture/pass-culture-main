import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, successData } from '../reducers/data'
import { assignErrors } from '../reducers/errors'
import { showNotification } from '../reducers/notification'
import { SUCCESS } from '../reducers/queries'
import { fetchData } from '../utils/request'


function* fromWatchRequestDataActions(action) {
  // UNPACK
  const {
    method,
    path,
    config
  } = action
  const {
    body,
    encode,
    hook,
    type
  } = (config || {})

  // TOKEN
  const token = yield type && select(state => state.data[`${type}Token`])

  // DATA
  try {

    // CALL
    const result = yield call(
      fetchData,
      method,
      path,
      { body, encode, token }
    )

    // HOOK
    if (hook) {
      yield call(hook, method, path, result, config)
    }

    // SUCCESS OR FAIL
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

function* fromWatchSuccessDataActions(action) {
  const {
    config,
    method
  } = action
  const {
    getNotification,
    redirect
  } = (config || {})

  // HOOK FOR A REDIRECT
  const isRedirect = config.isRedirect === false
                          ? false
                          : true
  if (isRedirect && redirect) {
    yield call(redirect, SUCCESS, action)
  }

  // HOOK FOR SOME NOTIFICATION
  const notification = getNotification && getNotification(SUCCESS, action)
  if (notification) {
    notification.type = 'success'
    yield put(showNotification(notification))
  }

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
  yield takeEvery(
    ({ type }) => /SUCCESS_DATA_(.*)/.test(type),
    fromWatchSuccessDataActions
  )
}
