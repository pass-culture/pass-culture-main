import { watchDataActions } from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchModalActions } from './modal'
import { watchFormActions } from './form'
import { watchUserActions } from './user'

function* rootSaga() {
  yield all([
    watchModalActions(),
    watchDataActions(),
    watchFormActions(),
    watchUserActions(),
  ])
}

export default rootSaga
