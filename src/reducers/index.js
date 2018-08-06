import { errors, form, loading, modal, user } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import data from './data'
import geolocation from './geolocation'
import { menu } from './menu'
import splash from './splash'
import verso from './verso'

const rootReducer = combineReducers({
  data,
  errors,
  form,
  geolocation,
  loading,
  menu,
  modal,
  splash,
  user,
  verso,
})

export default rootReducer
