import { all } from 'redux-saga/effects'

import { watchModalActions } from './modal'
import { watchDataActions } from './data'
import { watchUserActions } from './user'

function * rootSaga () {
  yield all([
    watchModalActions(),
    watchDataActions(),
    watchUserActions()
  ])
}

export default rootSaga
