import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

import { createDataReducer } from '../../utils/fetch-normalize-data/reducers/data/createDataReducer'

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
}

const dataReducer = createDataReducer({
  bookings: [],
  favorites: [],
  features: [],
  mediations: [],
  musicTypes: [],
  offers: [],
  showTypes: [],
  stocks: [],
  types: [],
})

const persistDataReducer = persistReducer(dataPersistConfig, dataReducer)

export default persistDataReducer
