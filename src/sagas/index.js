import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'

function* rootSaga() {
  yield all([
    watchDataActions(),
    watchErrorsActions(),
    watchFormActions(),
    watchModalActions(),
    watchUserActions(),
  ])
}

export default rootSaga
