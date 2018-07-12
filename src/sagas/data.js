import { call, put, select, takeEvery } from 'redux-saga/effects'

import { failData, successData } from '../reducers/data'
import { newErrorForm } from '../reducers/form'
import { assignErrors } from '../reducers/errors'
import { fetchData } from '../utils/request'

function* fromWatchRequestDataActions(action) {
  // UNPACK
  const {
    method,
    path,
    config
  } = action
  const {
    body,
    encode,
    type,
    formName,
  } = (config || {})

  // TOKEN
  const token = yield type && select(state => state.data[`${type}Token`])

  // DATA
  try {

    // CALL
    const result = yield call(
      fetchData,
      method,
      path,
      { body, encode, token }
    )

    // SUCCESS OR FAIL
    if (result.data) {
      yield put(successData(method, path, result.data, config))

    } else {
      if (formName) {
        yield put(newErrorForm(formName, result.errors))
      }
      yield put(failData(method, path, result.errors, config))
    }

  } catch (error) {
    console.warn('error', error)
    yield put(failData(method, path, [{
      //global: String(error)
      global: "Erreur serveur. Tentez de rafraîchir la page."
    }], config))
  }
}

function* fromWatchFailDataActions(action) {
  const errors = [].concat(action.errors)

  for (let error of errors) {
    yield put(assignErrors(error))
  }
  if (action.config.handleFail) {
    const state = yield select(state => state)
    yield call(action.config.handleFail, state, action)
  }
}

function* fromWatchSuccessDataActions(action) {
  if (action.config.handleSuccess) {
    const state = yield select(state => state)
    yield call(action.config.handleSuccess, state, action)
  }
}

export function* watchDataActions() {
  yield takeEvery(
    ({ type }) => /REQUEST_DATA_(.*)/.test(type),
    fromWatchRequestDataActions
  )
  yield takeEvery(
    ({ type }) => /FAIL_DATA_(.*)/.test(type),
    fromWatchFailDataActions
  )
  yield takeEvery(
    ({ type }) => /SUCCESS_DATA_(.*)/.test(type),
    fromWatchSuccessDataActions
  )
}
