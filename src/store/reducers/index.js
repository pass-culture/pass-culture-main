import { form, loading, notification, tracker } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import data from './data'
import errors from './errors'
import modal from './modal'
import bookingSummary from './bookingSummary/bookingSummary'
import maintenanceReducer from './maintenanceReducer'

const rootReducer = combineReducers({
  bookingSummary,
  data,
  errors,
  form,
  loading,
  modal,
  notification,
  tracker,
  maintenance: maintenanceReducer,
})

export default rootReducer
