import { call, put, select, takeEvery } from 'redux-saga/effects'

import { setUser } from '../reducers/user'
import { clear } from '../utils/dexie'
import registerSyncServiceWorker from '../utils/registerSyncServiceWorker'

let syncRegistration

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false
  yield put(setUser(false))
  yield call(clear)
  if (syncRegistration) {
    yield call(syncRegistration.unregister)
  }
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(setUser(null))
  yield call(clear)
  if (syncRegistration) {
    yield call(syncRegistration.unregister)
  }
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
    syncRegistration = yield call(registerSyncServiceWorker)
  }
}

export function * watchUserActions () {
  yield takeEvery(({ type }) =>
    /FAIL_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
    /FAIL_DATA_GET_USERS\/ME(.*)/.test(type), fromWatchFailSignActions)
  yield takeEvery(({ type }) =>
    /SUCCESS_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
    /SUCCESS_DATA_GET_USERS\/ME(.*)/.test(type), fromWatchSuccessSignActions)
  yield takeEvery(({ type }) =>
    /SUCCESS_DATA_GET_USERS\/SIGNOUT(.*)/.test(type), fromWatchSuccessGetSignoutActions)
}
