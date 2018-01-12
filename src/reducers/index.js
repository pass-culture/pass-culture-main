import { combineReducers } from 'redux'

import browser from './browser'
import data from './data'
import form from './form'
import modal from './modal'
import navigation from './navigation'
import user from './user'

const rootReducer = combineReducers({ browser,
  data,
  form,
  modal,
  navigation,
  user
})

export default rootReducer
