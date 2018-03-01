import { call, put, select, takeEvery } from 'redux-saga/effects'

import { resetData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { clear } from '../utils/dexie'
import { sync } from '../utils/registerDexieServiceWorker'

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false
  yield call(clear)
  yield put(setUser(false))
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(resetData())
  yield call(clear)
  yield put(setUser(false))
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
    yield call(sync, 'dexie-pull')
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
