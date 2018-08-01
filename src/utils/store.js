import { applyMiddleware, compose, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { routerMiddleware } from 'react-router-redux'

import init from './init'
import rootReducer from '../reducers'
import rootSaga from '../sagas'
import history from './history'

// MIDDLEWARES
const sagaMiddleware = createSagaMiddleware()
const middlewares = [sagaMiddleware, routerMiddleware(history)]

// ENHANCERS
const enhancers = []
const composeEnhancers =
  (typeof window !== 'undefined' &&
    // eslint-disable-next-line no-underscore-dangle
    window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) ||
  compose

const storeEnhancer = composeEnhancers(
  ...enhancers,
  applyMiddleware(...middlewares)
)

// STORE
const store = createStore(rootReducer, {}, storeEnhancer)

// RUN
sagaMiddleware.run(rootSaga)

// INIT
init(store)

// export
export default store
