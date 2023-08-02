import createStore from 'store'
import { initialState as featuresInitialState } from 'store/features/reducer'
import { initialState as offersInitialState } from 'store/offers/reducer'
import { initialState as maintenanceInitialState } from 'store/reducers/maintenanceReducer'
import { initialState as notificationInitialState } from 'store/reducers/notificationReducer'
import { initialState as userInitialState } from 'store/user/reducer'

export const configureTestStore = overrideData => {
  const initialData = {
    features: { ...featuresInitialState, initialized: true },
    maintenance: maintenanceInitialState,
    notification: notificationInitialState,
    offers: offersInitialState,
    user: userInitialState,
  }

  return createStore({ ...initialData, ...overrideData }).store
}
