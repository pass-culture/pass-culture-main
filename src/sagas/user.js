import Cookies from 'js-cookies'
import { call, put, select, takeEvery } from 'redux-saga/effects'

import { resetData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { clear } from '../utils/dexie'
import { sync } from '../utils/registerDexieServiceWorker'

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false or false to null
  yield call(clear)
  const user = yield select(state => state.user)
  yield put(setUser(user === false ? null : false))
  yield call(sync, 'dexie-signout')
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(resetData())
  yield call(clear)
  yield put(setUser(false))
  yield call(sync, 'dexie-signout')
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
    // call the dexie-user event
    // either the sync service worker has already in state the user
    // then it just sync the redux with the dexie state
    // else it asks for a dexie push pull to also feed
    // the dexie with the backend
    const rememberToken = Cookies.getItem('remember_token')
    yield call(sync, 'dexie-signin', { rememberToken, user })
  } else {
    yield call(fromWatchFailSignActions)
  }
}

export function * watchUserActions () {
  yield takeEvery(({ type }) =>
    /FAIL_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
    /FAIL_DATA_GET_USERS\/ME(.*)/.test(type), fromWatchFailSignActions)
  yield takeEvery(({ type }) =>
    /SUCCESS_DATA_POST_USERS/.test(type) ||
    /SUCCESS_DATA_GET_USERS\/ME(.*)/.test(type), fromWatchSuccessSignActions)
  yield takeEvery(({ type }) =>
    /SUCCESS_DATA_GET_USERS\/SIGNOUT(.*)/.test(type), fromWatchSuccessGetSignoutActions)
}
