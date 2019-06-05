import { applyMiddleware, combineReducers, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { all } from 'redux-saga/effects'
import { createData, watchDataActions } from 'redux-saga-data'

export function configureTestStore() {
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
    data: createData({ users: [] }),
  })

  const store = createStore(rootReducer, storeEnhancer)

  sagaMiddleware.run(rootSaga)

  return store
}

export default configureTestStore
