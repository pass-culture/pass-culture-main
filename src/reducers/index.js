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
import counter from './counter'

const rootReducer = combineReducers({
  counter,
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
