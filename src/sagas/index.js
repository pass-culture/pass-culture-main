import { all } from 'redux-saga/effects'

import { watchModalActions } from './modal'
import { watchRequestActions } from './request'
import { watchUserActions } from './user'

function * rootSaga () {
  yield all([
    watchModalActions(),
    watchRequestActions(),
    watchUserActions()
  ])
}

export default rootSaga
