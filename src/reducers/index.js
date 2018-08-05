import {
  blockers,
  errors,
  form,
  loading,
  modal,
  user,
} from 'pass-culture-shared'
import { combineReducers } from 'redux'

import data from './data'
import geolocation from './geolocation'
import verso from './verso'
import splash from './splash'

const rootReducer = combineReducers({
  blockers,
  data,
  errors,
  form,
  geolocation,
  loading,
  modal,
  splash,
  user,
  verso,
})

export default rootReducer
