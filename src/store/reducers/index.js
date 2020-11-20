import { combineReducers } from 'redux'

import { tracker } from 'store/reducers/tracker'

import { offersReducer } from '../offers/reducer'

import actionsBar from './actionsBar'
import bookingSummary from './bookingSummary/bookingSummary'
import data from './data'
import errors from './errors'
import { form } from './form'
import maintenanceReducer from './maintenanceReducer'
import modal from './modal'
import { notificationReducer } from './notificationReducer'

const rootReducer = combineReducers({
  actionsBar,
  bookingSummary,
  data,
  errors,
  form,
  modal,
  offers: offersReducer,
  notification: notificationReducer,
  tracker,
  maintenance: maintenanceReducer,
})

export default rootReducer
