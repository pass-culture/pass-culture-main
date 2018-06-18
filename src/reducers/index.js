import { combineReducers } from 'redux'

import data from './data'
import errors from './errors'
import form from './form'
import loading from './loading'
import modal from './modal'
import notification from './notification'
import queries from './queries'
import splash from './splash'
import user from './user'

const rootReducer = combineReducers({
  data,
  errors,
  form,
  loading,
  modal,
  notification,
  queries,
  splash,
  user,
})

export default rootReducer
