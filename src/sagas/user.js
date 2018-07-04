import moment from 'moment'
import { call, put, select, takeEvery } from 'redux-saga/effects'

import { resetData } from '../reducers/data'
import { setUser } from '../reducers/user'
import { clear } from '../workers/dexie/data'
import { worker } from '../workers/dexie/register'

function* fromWatchFailSignActions(action) {
  // force to update by changing value null to false or false to null
  yield call(clear)
  const currentUser = yield select(state => state.user)
  yield put(setUser(currentUser === false ? null : false))
}

function* fromWatchSuccessGetSignoutActions() {
  yield put(resetData())
  yield call(clear)
  yield put(setUser(false))
  worker.postMessage({ key: 'dexie-signout' })
}

function* fromWatchSuccessSignActions() {
  const user = yield select(state =>
    state.data.users && state.data.users[0]
  )
  const currentUser = yield select(state => state.user)
  const isDeprecatedCurrentUser =
    currentUser &&
    (user.id !== currentUser.id ||
      moment(user.dateCreated) > moment(currentUser.dateCreated))
  if (user && (!currentUser || isDeprecatedCurrentUser)) {
    // clear if the currentUser was deprecated
    if (isDeprecatedCurrentUser) {
      yield call(clear)
    }
    // set
    yield put(setUser(user))
    // call the dexie-user event
    // either the sync service worker has already in state the user
    // then it just sync the redux with the dexie state
    // else it asks for a dexie push pull to also feed
    // the dexie with the backend
    worker.postMessage({ key: 'dexie-signin', state: { user } })
  } else if (!user) {
    yield put(setUser(false))
  }
}

export function* watchUserActions() {
  yield takeEvery(
    ({ type }) =>
      /FAIL_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
      /FAIL_DATA_GET_USERS\/CURRENT(.*)/.test(type),
    fromWatchFailSignActions
  )
  yield takeEvery(
    ({ type }) =>
      /SUCCESS_DATA_POST_USERS/.test(type) ||
      /SUCCESS_DATA_GET_USERS\/CURRENT(.*)/.test(type),
    fromWatchSuccessSignActions
  )
  yield takeEvery(
    ({ type }) => /SUCCESS_DATA_GET_USERS\/SIGNOUT(.*)/.test(type),
    fromWatchSuccessGetSignoutActions
  )
}
