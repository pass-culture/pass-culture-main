import { API_URL } from 'utils/config'
import { all } from 'redux-saga/effects'
import { watchDataActions } from 'redux-saga-data'
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
