import { all } from 'redux-saga/effects'

import { watchRequestActions } from './request'
import { watchSuccessPostSignActions } from './user'

function * rootSaga () {
  yield all([
    watchRequestActions(),
    watchSuccessPostSignActions()
  ])
}

export default rootSaga
