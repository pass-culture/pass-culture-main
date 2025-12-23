import { combineReducers } from '@reduxjs/toolkit'

import { featuresReducer } from '@/commons/store/features/reducer'
import { offererReducer } from '@/commons/store/offerer/reducer'
import { snackBarReducer } from '@/commons/store/snackBar/reducer'
import { userReducer } from '@/commons/store/user/reducer'

import { adageFilterReducer } from './adageFilter/reducer'
import { navReducer } from './nav/reducer'
import { musicTypesReducer } from './staticData/reducer'

export const rootReducer = combineReducers({
  features: featuresReducer,
  snackBar: snackBarReducer,
  user: userReducer,
  nav: navReducer,
  adageFilter: adageFilterReducer,
  offerer: offererReducer,
  staticData: musicTypesReducer,
})
