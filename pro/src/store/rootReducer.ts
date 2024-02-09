import { combineReducers } from '@reduxjs/toolkit'

import { featuresReducer } from 'store/features/reducer'
import { notificationsReducer } from 'store/notifications/reducer'
import { offersReducer } from 'store/offers/reducer'
import { userReducer } from 'store/user/reducer'

const rootReducer = combineReducers({
  features: featuresReducer,
  offers: offersReducer,
  notification: notificationsReducer,
  user: userReducer,
})

export default rootReducer

export type RootState = ReturnType<typeof rootReducer>
