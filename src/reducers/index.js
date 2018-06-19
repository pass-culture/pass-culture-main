import { combineReducers } from 'redux'

import blockers from './blockers'
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
  blockers,
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
