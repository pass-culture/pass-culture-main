import { combineReducers } from 'redux'

import browser from './browser'
import request from './request'

const rootReducer = combineReducers({ browser,
  request
})

export default rootReducer
