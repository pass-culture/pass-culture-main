import {
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'
import { watchDataActions } from 'redux-saga-data'

import { watchFormActions } from './form'
import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([
    watchDataActions({
      rootUrl: API_URL,
      timeout: 50000,
    }),
    watchErrorsActions(),
    watchFormActions(),
    watchModalActions(),
    watchUserActions(),
  ])
}

export default rootSaga
