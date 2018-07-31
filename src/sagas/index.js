import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchFormActions } from './form'
import { watchUserActions as watchProActions } from './user'

function* rootSaga() {
  yield all([
    watchDataActions(),
    watchErrorsActions(),
    watchFormActions(),
    watchModalActions(),
    watchProActions(),
    watchUserActions(),
  ])
}

export default rootSaga
