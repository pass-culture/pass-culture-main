import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { createDataReducer } from 'redux-saga-data'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  whitelist: ['readRecommendations'],
}

const dataReducer = createDataReducer({
  bookings: [],
  readRecommendations: [],
  recommendations: [],
  types: [],
  users: [],
})

const data = persistReducer(dataPersistConfig, dataReducer)

export default data
