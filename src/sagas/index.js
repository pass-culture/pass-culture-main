import {
  watchDataActions,
  watchErrorsActions,
  watchModalActions,
  watchUserActions,
} from 'pass-culture-shared'
import { all } from 'redux-saga/effects'

function* rootSaga() {
  yield all([
    watchModalActions(),
    watchDataActions(),
    watchErrorsActions(),
    watchUserActions(),
  ])
}

export default rootSaga
