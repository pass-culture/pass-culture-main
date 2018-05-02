import { combineReducers } from 'redux'

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
  user
})

export default rootReducer
