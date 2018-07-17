import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'

//import data from './data'
import { data } from 'shared/reducers/data'
import form from './form'
import geolocation from './geolocation'
import loading from './loading'
import modal from './modal'
import queries from './queries'
import verso from './verso'
import splash from './splash'
import user from './user'

const rootReducer = combineReducers({
  data,
  form,
  geolocation,
  loading,
  modal,
  queries,
  splash,
  verso,
  user,
  router: routerReducer,
})

export default rootReducer
