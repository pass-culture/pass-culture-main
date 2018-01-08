import { combineReducers } from 'redux'

import browser from './browser'
import modal from './modal'
import request from './request'

const rootReducer = combineReducers({ browser,
  modal,
  request
})

export default rootReducer
