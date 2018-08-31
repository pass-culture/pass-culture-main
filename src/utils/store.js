/* eslint
  no-underscore-dangle: 0
*/
import createSagaMiddleware from 'redux-saga'
// defaults to localStorage for web and AsyncStorage for react-native
import storage from 'redux-persist/lib/storage'
import { persistStore, persistReducer } from 'redux-persist'
import { compose, createStore, applyMiddleware } from 'redux'

import rootSaga from '../sagas'
import rootReducer from '../reducers'
import initGeolocation from './initGeolocation'
import { PERSIST_STORE_KEY, PERSIST_WHITE_LIST } from './config'

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

const buildStoreReducers = () => {
  // FIXME -> sortir la configuration de redux-persist
  // pour pouvoir faire les tests unitaires sur le store
  const persistConfig = {
    key: PERSIST_STORE_KEY,
    storage,
    whitelist: PERSIST_WHITE_LIST,
  }
  return persistReducer(persistConfig, rootReducer)
}

// NOTE -> Il est important d'encapsuler la creation des stores
// dans une function pour les tests unitaires
export const configureStore = (initialState = {}) => {
  const sagaMiddleware = createSagaMiddleware()
  const storeReducers = buildStoreReducers()
  const store = createStore(
    storeReducers,
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
