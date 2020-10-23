import { watchDataActions } from 'redux-saga-data'
import { all } from 'redux-saga/effects'

import { API_URL } from 'utils/config'

import { watchErrorsActions } from './errors'
import { watchModalActions } from './modal'

function* rootSaga() {
  yield all([
    watchDataActions({
      rootUrl: API_URL,
      timeout: 50000,
    }),
    watchErrorsActions(),
    watchModalActions(),
  ])
}

export default rootSaga
