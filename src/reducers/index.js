import { combineReducers } from 'redux'
import data, { lastRecommendationsRequestTimestamp } from './data'
import geolocation from './geolocation'
import menu from './menu'
import overlay from './overlay'
import pagination from './pagination'
import share from './share'
import splash from './splash'
import token from './token'
import maintenanceReducer from './maintenanceReducer'

const rootReducer = combineReducers({
  data,
  geolocation,
  lastRecommendationsRequestTimestamp,
  maintenance: maintenanceReducer,
  menu,
  overlay,
  pagination,
  share,
  splash,
  token,
})

export default rootReducer
