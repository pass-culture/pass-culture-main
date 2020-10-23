import { applyMiddleware, combineReducers, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { createDataReducer, watchDataActions } from 'redux-saga-data'
import { all } from 'redux-saga/effects'

export const configureTestStore = () => {
  const sagaMiddleware = createSagaMiddleware()
  const storeEnhancer = applyMiddleware(sagaMiddleware)

  function* rootSaga() {
    yield all([
      watchDataActions({
        rootUrl: 'http://foo.com',
      }),
    ])
  }

  const rootReducer = combineReducers({
    data: createDataReducer({ users: [] }),
  })

  const store = createStore(rootReducer, storeEnhancer)

  sagaMiddleware.run(rootSaga)

  return store
}

export const configureFetchCurrentUserWithLoginFail = () =>
  fetch.mockResponse(
    JSON.stringify([{ global: ['Nobody is authenticated here'] }]),
    { status: 400 }
  )

export const configureFetchCurrentUserWithLoginSuccess = () =>
  fetch.mockResponse(JSON.stringify({ email: 'michel.marx@youpi.fr', hasOffers: false, hasPhysicalVenues: false }), {
    status: 200,
  })

export const configureFetchCurrentUserWithLoginSuccessAndOffers = () =>
  fetch.mockResponse(JSON.stringify({ email: 'michel.marx@youpi.fr', hasOffers: true, hasPhysicalVenues: true  }), {
    status: 200,
  })

export default configureTestStore
