import storage from 'redux-persist/lib/storage' // defaults to localStorage for web and AsyncStorage for react-native

const persist = {
  key: 'pro-passculture',
  storage,
  whitelist: ['data', 'errors', 'tracker', 'user'],
}

export default persist
