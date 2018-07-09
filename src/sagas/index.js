import { watchDataActions } from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

import { watchModalActions } from './modal'
import { watchUserActions } from './user'

function* rootSaga() {
  yield all([
    watchModalActions(),
    watchDataActions(),
    watchUserActions()
  ])
}

export default rootSaga
