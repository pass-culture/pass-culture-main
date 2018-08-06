import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native

const persist = {
  key: 'app-passculture',
  storage,
  whitelist: ['data', 'errors', 'user'],
}

export default persist
