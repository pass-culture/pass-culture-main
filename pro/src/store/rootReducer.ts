import { combineReducers } from '@reduxjs/toolkit'

import { featuresReducer } from 'store/features/reducer'
import { notificationsReducer } from 'store/notifications/reducer'
import { userReducer } from 'store/user/reducer'

import { adageFilterReducer } from './adageFilter/reducer'
import { navReducer } from './nav/reducer'

export const rootReducer = combineReducers({
  features: featuresReducer,
  notification: notificationsReducer,
  user: userReducer,
  nav: navReducer,
  adageFilter: adageFilterReducer,
})

export type RootState = ReturnType<typeof rootReducer>
