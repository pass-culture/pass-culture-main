import { form, loading, notification, tracker } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import bookingSummary from './bookingSummary/bookingSummary'
import data from './data'
import errors from './errors'
import maintenanceReducer from './maintenanceReducer'
import modal from './modal'

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
