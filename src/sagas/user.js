import { put, select, takeEvery } from 'redux-saga/effects'

import { setUser } from '../reducers/user'

function * fromWatchFailPostSignActions (action) {
  // console.log('action', action)
  // yield put(set)
}

function * fromWatchSuccessPostSignActions () {
  const user = yield select(state => state.data.users && state.data.users[0])
  if (user) {
    yield put(setUser(user))
  }
}

export function * watchUserActions () {
  yield takeEvery(({ type }) =>
    /FAIL_DATA_POST_USERS\/SIGN(.*)/.test(type), fromWatchFailPostSignActions)
  yield takeEvery(({ type }) =>
    /SUCCESS_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
    /SUCCESS_DATA_GET_USERS\/ME(.*)/.test(type), fromWatchSuccessPostSignActions)
}
