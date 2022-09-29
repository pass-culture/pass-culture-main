import { applyMiddleware, compose, createStore } from 'redux'
import thunk from 'redux-thunk'

import rootReducer from './reducers'

const buildStoreEnhancer = (middlewares = []) => {
  const enhancers = []

  const useDevTools =
    typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
  if (useDevTools) {
    const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
    return composeEnhancers(...enhancers, applyMiddleware(...middlewares))
  }

  return compose(...enhancers, applyMiddleware(...middlewares))
}

const configureStore = (initialState = {}) => {
  const store = createStore(
    rootReducer,
    initialState,
    buildStoreEnhancer([thunk])
  )

  return { store }
}

export default configureStore
