import { all } from 'redux-saga/effects'

import { watchRequestActions } from './request'

function * rootSaga () {
  yield all([
    watchRequestActions()
  ])
}

export default rootSaga
