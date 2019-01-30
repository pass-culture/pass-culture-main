import { errors, form, loading, modal, user } from 'pass-culture-shared'
import { combineReducers } from 'redux'

import data from './data'
import geolocation from './geolocation'
import { menu } from './menu'
import { share } from './share'
import splash from './splash'
import card from './card'
import { overlay } from './overlay'

const rootReducer = combineReducers({
  card,
  data,
  errors,
  form,
  geolocation,
  loading,
  menu,
  modal,
  overlay,
  share,
  splash,
  user,
})

export default rootReducer
