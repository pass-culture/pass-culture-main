import { form, loading, tracker } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import actionsBar from './actionsBar'
import bookingSummary from './bookingSummary/bookingSummary'
import data from './data'
import errors from './errors'
import maintenanceReducer from './maintenanceReducer'
import modal from './modal'
import { notificationReducer } from './notificationReducer'
import offers from './offers'

const rootReducer = combineReducers({
  actionsBar,
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
