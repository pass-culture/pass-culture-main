import { call, put, takeLatest } from 'redux-saga/effects'
import { fetchData } from 'pass-culture-shared'
import {
  COUNTER_GET_VERIFICATION,
  receiveVerification,
} from '../reducers/counter'

function getBooking(id) {
  return fetchData('GET', `/bookings/${id}`, {
    url: 'http://localhost',
  })
}

function* counterGetVerification(action) {
  const response = yield call(getBooking, action.payload)
  yield put(receiveVerification(200, response.data))
}

function* watchCounterActions() {
  console.log('cunter sagas init')
  yield [takeLatest(COUNTER_GET_VERIFICATION, counterGetVerification)]
}

export default watchCounterActions
