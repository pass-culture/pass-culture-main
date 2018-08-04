import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native

const persist = {
  key: 'app.passculture.beta.gouv.fr',
  storage,
}

export default persist
