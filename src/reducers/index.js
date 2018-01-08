import { combineReducers } from 'redux'

import browser from './browser'
import form from './form'
import modal from './modal'
import request from './request'

const rootReducer = combineReducers({ browser,
  form,
  modal,
  request
})

export default rootReducer
