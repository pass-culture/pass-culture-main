import { call, put, select, takeEvery } from 'redux-saga/effects'

import { requestData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { clear } from '../utils/dexie'

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false
  yield put(setUser(false))
  yield call(clear)
  // this will download examples of userMediations
  // for not connected user
  yield put(requestData('PUT', 'userMediations', { sync: true }))
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(setUser(null))
  yield call(clear)
  // this will download examples of userMediations
  // for not connected user
  yield put(requestData('PUT', 'userMediations', { sync: true }))
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
    // that one will fetch specified userMediations
    yield put(requestData('PUT', 'userMediations', { sync: true }))
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
