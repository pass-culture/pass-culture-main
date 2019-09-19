import { all } from 'redux-saga/effects'
import { watchDataActions } from 'redux-saga-data'

import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([watchDataActions({ rootUrl: API_URL })])
}

export default rootSaga
