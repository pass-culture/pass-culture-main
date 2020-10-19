import { form, loading, tracker } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import bookingSummary from './bookingSummary/bookingSummary'
import data from './data'
import errors from './errors'
import maintenanceReducer from './maintenanceReducer'
import modal from './modal'
import offers from './offers'
import { notificationReducer } from './notificationReducer'

const rootReducer = combineReducers({
  bookingSummary,
  data,
  errors,
  form,
  loading,
  modal,
  offers,
  notification: notificationReducer,
  tracker,
  maintenance: maintenanceReducer,
})

export default rootReducer
