import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, successData } from '../reducers/data'
import { assignErrors } from '../reducers/errors'
import { setNotification } from '../reducers/notification'
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
  console.log('action ---- ', action);
  const isNotification = action.config.isNotification === false
  ? false : true
  const notification = action.config.getNotification && action.config.getNotification(SUCCESS)
  notification.type = SUCCESS

   if  (isNotification && notification && (action.method === 'POST' || action.method === 'PATCH')) {
     yield put(setNotification(notification))
   }
//   if (isRedirect  && redirectPathname) {
//     yield call(history.push, redirectPathname) }
//    }
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
  // yield takeEvery(
  //   ({ type }) => /SUCCESS_DATA_(.*)/.test(type),
  //   fromWatchSuccessDataActions
  // )
}
