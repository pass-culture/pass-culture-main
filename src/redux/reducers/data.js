import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

import createDataReducer from '../../utils/fetch-normalize-data/reducers/data/createDataReducer'

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
