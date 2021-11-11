/*
* @debt deprecated "Gaël: deprecated usage of redux-saga-data"
*/

import { watchDataActions } from 'redux-saga-data'
import { all } from 'redux-saga/effects'

import { API_URL } from 'utils/config'

import { watchErrorsActions } from './errors'

function* rootSaga() {
  yield all([
    watchDataActions({
      rootUrl: API_URL,
      timeout: 50000,
    }),
    watchErrorsActions(),
  ])
}

export default rootSaga
