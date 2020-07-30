import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { createDataReducer } from 'redux-thunk-data'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  whitelist: ['readRecommendations'],
}

const dataReducer = createDataReducer({
  bookings: [],
  favorites: [],
  features: [],
  mediations: [],
  musicTypes: [],
  offers: [],
  readRecommendations: [],
  recommendations: [],
  searchedRecommendations: [],
  showTypes: [],
  stocks: [],
  types: [],
})

const persistDataReducer = persistReducer(dataPersistConfig, dataReducer)

export default persistDataReducer
