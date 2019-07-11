import createSagaMiddleware from 'redux-saga'
import { persistStore } from 'redux-persist'
import { compose, createStore, applyMiddleware } from 'redux'

import rootSaga from '../sagas'
import rootReducer from '../reducers'
import initGeolocation from './initGeolocation'

const buildStoreEnhancer = (middlewares = []) => {
  const enhancers = []
  // utilisation de l'extension browser react-dev-tools
  const useDevTools =
    typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
  if (useDevTools) {
    const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
    return composeEnhancers(...enhancers, applyMiddleware(...middlewares))
  }
  return compose(
    ...enhancers,
    applyMiddleware(...middlewares)
  )
}

// NOTE -> Il est important d'encapsuler la creation des stores
// dans une function pour les tests unitaires
export const configureStore = (initialState = {}) => {
  const sagaMiddleware = createSagaMiddleware()
  const store = createStore(
    rootReducer,
    initialState,
    buildStoreEnhancer([sagaMiddleware])
  )
  const persistor = persistStore(store)
  // lancement de la premiere saga
  sagaMiddleware.run(rootSaga)
  // lancement de la geolocalisation de l'user
  initGeolocation(store)
  return { persistor, store }
}

export default configureStore
