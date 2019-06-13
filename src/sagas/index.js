import { all } from 'redux-saga/effects'
import { watchModalActions } from 'redux-react-modals'
import { watchDataActions } from 'redux-saga-data'

import { API_URL } from '../utils/config'

function* rootSaga() {
  yield all([watchModalActions(), watchDataActions({ rootUrl: API_URL })])
}

export default rootSaga
