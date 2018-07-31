import { requestData, SET_USER, showModal } from 'pass-culture-shared'
import React from 'react'
import { put, select, takeEvery } from 'redux-saga/effects'

import offerersSelector from '../selectors/offerers'

function* fromWatchSetUserActions(action) {
  const offerers = yield select(offerersSelector)

  if (action.user && !offerers.length) {
    yield put(
      showModal(
        <div>
          Cet utilisateur {action.user.publicName} n'est pas permis sur cette
          plateforme{' '}
        </div>
      ),
      {
        onCloseClick: function*() {
          yield put(requestData('GET', 'users/signout'))
        },
      }
    )
  }
}

export function* watchUserActions() {
  yield takeEvery(SET_USER, fromWatchSetUserActions)
}
