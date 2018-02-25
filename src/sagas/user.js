import { call, put, select, takeEvery } from 'redux-saga/effects'

import { resetData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { IS_DEV } from '../utils/config'
import { clear, pull } from '../utils/dexie'
import registerDexieServiceWorker from '../utils/registerDexieServiceWorker'

let dexieRegistration

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false
  yield put(setUser(false))
  yield call(clear)
  if (dexieRegistration) {
    yield call(dexieRegistration.unregister)
  }
  yield put(resetData)
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(setUser(null))
  yield call(clear)
  if (dexieRegistration) {
    yield call(dexieRegistration.unregister)
  }
  yield put(resetData)
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    dexieRegistration = yield call(registerDexieServiceWorker)
    //yield call(pull, { userMediations: 'unread' })
    yield put(setUser(user))
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

if (IS_DEV) {
  window.consoleDexie = function () {
    console.log(dexieRegistration)
  }
  window.unregisterDexie = function () {
    dexieRegistration && dexieRegistration.unregister()
    dexieRegistration = null
  }
}
