import {
  blockers,
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

const rootReducer = combineReducers({
  blockers,
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
