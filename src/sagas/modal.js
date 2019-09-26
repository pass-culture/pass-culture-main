import { takeEvery } from 'redux-saga/effects'

import { CLOSE_MODAL, SHOW_MODAL } from '../reducers/modal'

export function fromWatchCloseModalAction() {
  document.body.style.overflow = 'initial'
}

export function fromWatchShowModalAction() {
  document.body.style.overflow = 'hidden'
}

export function* watchModalActions() {
  yield takeEvery(CLOSE_MODAL, fromWatchCloseModalAction)
  yield takeEvery(SHOW_MODAL, fromWatchShowModalAction)
}
