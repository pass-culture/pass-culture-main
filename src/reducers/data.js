import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { createData } from 'redux-saga-data'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  whitelist: ['readRecommendations'],
}

const dataReducer = createData({
  bookings: [],
  readRecommendations: [],
  recommendations: [],
  types: [],
  users: [],
})

const data = persistReducer(dataPersistConfig, dataReducer)

export default data
