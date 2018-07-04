import moment from 'moment'
import { put,
  select,
  takeEvery
} from 'redux-saga/effects'

import { resetData } from '../reducers/data'
import { setUser } from '../reducers/user'

function* fromWatchRequestSignActions(action) {
  yield put(setUser(false)) // false while querying
}

function* fromWatchFailSignActions(action) {
  yield put(setUser(null)) // null otherwise
}

function* fromWatchSuccessGetSignoutActions() {
  yield put(resetData())
  yield put(setUser(null))
}

function* fromWatchSuccessSignActions() {
  const user = yield select(state => state.data.users && state.data.users[0])
  const currentUser = yield select(state => state.user)
  const isDeprecatedCurrentUser =
    currentUser &&
    (user.id !== currentUser.id ||
      moment(user.dateCreated) > moment(currentUser.dateCreated))
  if (user && (!currentUser || isDeprecatedCurrentUser)) {
    yield put(setUser(user))
  } else if (!user) {
    yield put(setUser(false))
  }
}

export function* watchUserActions() {
  yield takeEvery(
    ({ type }) =>
      /REQUEST_DATA_POST_USERS\/SIGN(.*)/.test(type) ||
      /REQUEST_DATA_GET_USERS\/CURRENT(.*)/.test(type),
    fromWatchRequestSignActions
  )
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
