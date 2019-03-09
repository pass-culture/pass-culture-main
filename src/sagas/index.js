import {
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'
import { watchDataActions } from 'redux-saga-data'

import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([
    watchModalActions(),
    watchDataActions({ rootUrl: API_URL }),
    watchErrorsActions(),
    watchUserActions(),
  ])
}

export default rootSaga
