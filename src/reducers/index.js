import {
  blockers,
  errors,
  form,
  loading,
  modal,
  notification,
  user
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
  user,
})

export default rootReducer
