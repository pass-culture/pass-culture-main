import { combineReducers } from 'redux'

import { appReducer } from 'store/app/reducer'
import { featuresReducer } from 'store/features/reducer'
import { offersReducer } from 'store/offers/reducer'
import { userReducer } from 'store/user/reducer'

import maintenanceReducer from './maintenanceReducer'
import { notificationReducer } from './notificationReducer'

const rootReducer = combineReducers({
  app: appReducer,
  features: featuresReducer,
  offers: offersReducer,
  notification: notificationReducer,
  user: userReducer,
  maintenance: maintenanceReducer,
})

export default rootReducer

export type RootState = ReturnType<typeof rootReducer>
