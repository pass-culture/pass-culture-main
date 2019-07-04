import {
  errors,
  form,
  loading,
  modal,
  notification,
  tracker,
  user,
} from 'pass-culture-shared'
import { combineReducers } from 'redux'

import data from './data'
import bookingSummary from './bookingSummary/bookingSummary'

const rootReducer = combineReducers({
  bookingSummary,
  data,
  errors,
  form,
  loading,
  modal,
  notification,
  tracker,
  user,
})

export default rootReducer
