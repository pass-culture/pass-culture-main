import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'

import browser from './browser'
import data from './data'
import form from './form'
import geolocation from './geolocation'
import loading from './loading'
import modal from './modal'
import verso from './verso'
import splash from './splash'
import user from './user'

const rootReducer = combineReducers({ browser,
  data,
  form,
  geolocation,
  loading,
  modal,
  splash,
  verso,
  user,
  router: routerReducer,
})

export default rootReducer
