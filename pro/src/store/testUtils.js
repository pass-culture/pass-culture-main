import { initialState as appInitialState } from 'store/app/reducer'
import { initialState as bookingSummaryInitialState } from 'store/reducers/bookingSummary/bookingSummary'
import configureStore from 'store'
import { initialState as errorsInitialState } from 'store/reducers/errors'
import { initialState as featuresInitialState } from 'store/features/reducer'
import { initialState as maintenanceInitialState } from 'store/reducers/maintenanceReducer'
import merge from 'lodash.merge'
import { initialState as notificationInitialState } from 'store/reducers/notificationReducer'
import { initialState as offersInitialState } from 'store/offers/reducer'
import { initialState as userInitialState } from 'store/user/reducer'

export const configureTestStore = overrideData => {
  const initialData = {
    app: { ...appInitialState, logEvent: jest.fn() },
    bookingSummary: bookingSummaryInitialState,
    features: { ...featuresInitialState, initialized: true },
    errors: errorsInitialState,
    maintenance: maintenanceInitialState,
    notification: notificationInitialState,
    offers: offersInitialState,
    user: userInitialState,
  }

  return configureStore(merge({}, initialData, overrideData)).store
}
