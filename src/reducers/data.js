import { createData } from 'pass-culture-shared'
import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  whitelist: ['seenRecommendations'],
}

const dataReducer = createData({
  bookings: [],
  recommendations: [],
  seenRecommendations: [],
  types: [],
  users: [],
})

const data = persistReducer(dataPersistConfig, dataReducer)

export default data
