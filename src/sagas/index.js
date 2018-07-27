import {
  watchDataActions,
  watchErrorsActions,
  watchUserActions
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'
import { watchModalActions } from './modal'

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
