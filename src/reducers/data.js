import { createData } from 'pass-culture-shared'
import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  whitelist: ['readRecommendations'],
}

const dataReducer = createData({
  bookings: [],
  readRecommendations: [],
  recommendations: [],
  seenRecommendations: [],
  types: [],
  users: [],
})

const data = persistReducer(dataPersistConfig, dataReducer)

export default data
