import { applyMiddleware, compose, createStore } from 'redux'
import { persistReducer, persistStore } from 'redux-persist'
import createSagaMiddleware from 'redux-saga'

import persist from './persist'
import rootReducer from '../reducers'
import rootSaga from '../sagas'

const buildStoreEnhancer = (middlewares = []) => {
  const enhancers = []

  const useDevTools = typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
  if (useDevTools) {
    const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
    return composeEnhancers(...enhancers, applyMiddleware(...middlewares))
  }

  return compose(
    ...enhancers,
    applyMiddleware(...middlewares)
  )
}

const configureStore = (initialState = {}) => {
  const sagaMiddleware = createSagaMiddleware()

  const persistedReducer = persistReducer(persist, rootReducer)

  const store = createStore(persistedReducer, initialState, buildStoreEnhancer([sagaMiddleware]))

  const persistor = persistStore(store)

  sagaMiddleware.run(rootSaga)

  return { persistor, store }
}

export default configureStore
