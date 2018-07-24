import { data, errors, form } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import blockers from './blockers'
import loading from './loading'
import modal from './modal'
import notification from './notification'
import queries from './queries'
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
  user,
})

export default rootReducer
