import { combineReducers } from 'redux'

import { appReducer } from 'store/app/reducer'
import { featuresReducer } from 'store/features/reducer'
import { offersReducer } from 'store/offers/reducer'
import { tracker } from 'store/reducers/tracker'

import bookingSummary from './bookingSummary/bookingSummary'
import data from './data'
import errors from './errors'
import maintenanceReducer from './maintenanceReducer'
import { notificationReducer } from './notificationReducer'

const rootReducer = combineReducers({
  app: appReducer,
  bookingSummary,
  data,
  errors,
  features: featuresReducer,
  offers: offersReducer,
  notification: notificationReducer,
  tracker,
  maintenance: maintenanceReducer,
})

export default rootReducer
