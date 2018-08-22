import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'
import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([
    watchDataActions({
      timeout: 10000,
      url: API_URL,
    }),
    watchErrorsActions(),
    watchFormActions(),
    watchModalActions(),
    watchUserActions(),
  ])
}

export default rootSaga
