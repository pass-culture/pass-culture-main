import { put, takeEvery } from 'redux-saga/effects'

import { setUser } from '../reducers/user'

function * fromWatchSuccessPostSignActions (action) {
  const { data } = action
  if (data && data.length === 1) {
    yield put(setUser(data[0]))
  }
}

export function * watchUserActions () {
  yield takeEvery(({ type }) =>
    /SUCCESS_POST_SIGN(.*)/.test(type), fromWatchSuccessPostSignActions)
}
