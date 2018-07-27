import { errors, form, user } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import blockers from './blockers'
import data from './data'
import loading from './loading'
import modal from './modal'
import notification from './notification'
import queries from './queries'

const rootReducer = combineReducers({
  blockers,
  data,
  errors,
  form,
  loading,
  modal,
  notification,
  queries,
  user,
})

export default rootReducer
