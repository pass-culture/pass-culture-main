import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'
import watchCounterActions from './counter'
import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([
    watchDataActions({
      timeout: 50000,
      url: API_URL,
    }),
    watchErrorsActions(),
    watchFormActions(),
    watchModalActions(),
    watchUserActions(),
    watchCounterActions(),
  ])
}

export default rootSaga
