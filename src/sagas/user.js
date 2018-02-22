import { call, put, select, takeEvery } from 'redux-saga/effects'

import { requestData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { clearUserMediations, putUserMediations } from '../utils/sync'

function * fromWatchFailSignActions (action) {
  // force to update by changing value null to false
  yield put(setUser(false))
  yield call(clearUserMediations)
}

function * fromWatchSuccessGetSignoutActions () {
  yield put(setUser(null))
  yield call(clearUserMediations)
}

function * fromWatchSuccessSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
    yield put(requestData('POST', 'userMediations', { hook: putUserMediations }))
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
