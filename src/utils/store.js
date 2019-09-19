import { applyMiddleware, compose, createStore } from 'redux'
import { persistStore } from 'redux-persist'
import thunk from 'redux-thunk'

import initGeolocation from './initGeolocation'
import rootReducer from '../reducers'
import { API_URL } from '../utils/config'

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

export const configureStore = (initialState = {}) => {
  const middlewares = [thunk.withExtraArgument({ rootUrl: API_URL })]

  const storeEnhancer = buildStoreEnhancer(middlewares)

  const store = createStore(rootReducer, initialState, storeEnhancer)

  const persistor = persistStore(store)

  initGeolocation(store)

  return { persistor, store }
}

export default configureStore
