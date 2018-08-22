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
import { PERSIST_STORE_KEY } from './config'

const buildStoreEnhancer = (middlewares = []) => {
  const enhancers = []
  let composeEnhancers = compose
  // utilisation de l'extension browser react-dev-tools
  if (typeof window !== 'undefined') {
    composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__
  }
  return composeEnhancers(...enhancers, applyMiddleware(...middlewares))
}

const buildStoreReducers = () => {
  // FIXME -> sortir la configuration du de redux-persist
  // pour pouvoir faire les tests unitaires sur le store
  const persistStoreWhiteList = ['user']
  const persistConfig = {
    key: PERSIST_STORE_KEY,
    storage,
    whitelist: persistStoreWhiteList,
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
