import { persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import { createDataReducer } from 'redux-saga-data'

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
  features: null,
  readRecommendations: [],
  recommendations: [],
  types: [],
  users: [],
})

const persistDataReducer = persistReducer(dataPersistConfig, dataReducer)

// ACTIONS CREATORS
export const saveLastRecommendationsRequestTimestamp = () => ({
  type: SAVE_RECOMMENDATIONS_REQUEST_TIMESTAMP,
})

export default persistDataReducer
