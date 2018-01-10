import { combineReducers } from 'redux'

import browser from './browser'
import form from './form'
import modal from './modal'
import navigation from './navigation'
import request from './request'
import user from './user'

const rootReducer = combineReducers({ browser,
  form,
  modal,
  navigation,
  request,
  user
})

export default rootReducer
