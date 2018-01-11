import { call, put, select, takeEvery } from 'redux-saga/effects'

import { CLOSE_MODAL, SHOW_MODAL } from '../reducers/modal'

function * fromWatchCloseModalAction (action) {
  document.body.style.overflow = 'scroll'
}

function * fromWatchShowModalAction (action) {
  document.body.style.overflow = 'hidden'
}

export function * watchModalActions () {
  yield takeEvery(CLOSE_MODAL, fromWatchCloseModalAction)
  yield takeEvery(SHOW_MODAL, fromWatchShowModalAction)
}
