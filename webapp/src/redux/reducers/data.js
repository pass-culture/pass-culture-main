import { createTransform, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'

import { createDataReducer } from '../../utils/fetch-normalize-data/reducers/data/createDataReducer'

const clearFeaturesOnRehydrate = createTransform(
  null,
  // transform state being rehydrated
  () => [],
  // define which reducers this transform gets called for.
  {
    whitelist: 'features',
  }
)

const dataPersistConfig = {
  key: 'passculture-webapp-data',
  storage,
  transforms: [clearFeaturesOnRehydrate],
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
