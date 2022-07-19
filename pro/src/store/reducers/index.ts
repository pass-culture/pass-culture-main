import { appReducer } from 'store/app/reducer'
import bookingSummary from './bookingSummary/bookingSummary'
import { combineReducers } from 'redux'
import errors from './errors'
import { featuresReducer } from 'store/features/reducer'
import maintenanceReducer from './maintenanceReducer'
import { notificationReducer } from './notificationReducer'
import { offersReducer } from 'store/offers/reducer'
import { userReducer } from 'store/user/reducer'

const rootReducer = combineReducers({
  app: appReducer,
  bookingSummary,
  errors,
  features: featuresReducer,
  offers: offersReducer,
  notification: notificationReducer,
  user: userReducer,
  maintenance: maintenanceReducer,
})

export default rootReducer

export type RootState = ReturnType<typeof rootReducer>
