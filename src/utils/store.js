import { applyMiddleware, compose, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'

import rootReducer from '../reducers'
import rootSaga from '../sagas'

const sagaMiddleware = createSagaMiddleware()
const middlewares = [sagaMiddleware]

const enhancers = []
const composeEnhancers =
  (typeof window !== 'undefined' &&
    window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) ||
  compose

const storeEnhancer = composeEnhancers(
  ...enhancers,
  applyMiddleware(...middlewares)
)

const store = createStore(rootReducer, {}, storeEnhancer)

sagaMiddleware.run(rootSaga)

export default store
