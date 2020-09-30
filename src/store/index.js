import { applyMiddleware, compose, createStore } from 'redux'
import { persistReducer, persistStore } from 'redux-persist'
import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native
import createSagaMiddleware from 'redux-saga'

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

  const persist = {
    key: 'pro-passculture',
    storage,
    whitelist: [
      'tracker',
    ],
  }

  const persistedReducer = persistReducer(persist, rootReducer)

  const store = createStore(persistedReducer, initialState, buildStoreEnhancer([sagaMiddleware]))

  const persistor = persistStore(store)

  sagaMiddleware.run(rootSaga)

  return { persistor, store }
}

export default configureStore
