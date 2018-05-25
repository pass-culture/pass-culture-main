import { combineReducers } from 'redux'
import { routerReducer } from 'react-router-redux'

import data from './data'
import form from './form'
import loading from './loading'
import modal from './modal'
import queries from './queries'
import splash from './splash'
import user from './user'

const rootReducer = combineReducers({
  data,
  form,
  loading,
  modal,
  queries,
  splash,
  user,
  router: routerReducer,
})

export default rootReducer
