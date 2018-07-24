import {
  watchDataActions,
  watchErrorsActions
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'
import { watchModalActions } from './modal'
import { watchUserActions } from './user'

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
