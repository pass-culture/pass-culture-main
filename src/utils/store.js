import { applyMiddleware, compose, createStore } from 'redux'
import createSagaMiddleware from 'redux-saga'
import { persistReducer } from 'redux-persist'

import persist from './persist'
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

const persistedReducer = persistReducer(persist, rootReducer)

const store = createStore(persistedReducer, {}, storeEnhancer)

sagaMiddleware.run(rootSaga)

export default store
