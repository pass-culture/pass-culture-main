import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { assignData, createDataReducer } from 'redux-saga-data'

export const SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP = 'SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP'

const initialState = 0
export const lastRecommendationsRequestTimestamp = (state = initialState, action) => {
  switch (action.type) {
    case SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP:
      return Date.now()
    default:
      return state
  }
}

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
  offers: [],
  readRecommendations: [],
  recommendations: [],
  stocks: [],
  types: [],
  users: [],
})

export const resetPageData = () =>
  assignData({
    bookings: [],
    favorites: [],
    mediations: [],
    offers: [],
    recommendations: [],
    stocks: [],
  })

const persistDataReducer = persistReducer(dataPersistConfig, dataReducer)

// ACTIONS CREATORS
export const saveLastRecommendationsRequestTimestamp = () => ({
  type: SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP,
})

export default persistDataReducer
