import { all } from 'redux-saga/effects'

import { watchModalActions } from './modal'
import { watchDataActions } from './data'
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
