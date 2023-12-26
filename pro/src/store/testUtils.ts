import { initialState as featuresInitialState } from 'store/features/reducer'
import { initialState as notificationInitialState } from 'store/notifications/reducer'
import { initialState as offersInitialState } from 'store/offers/reducer'
import createStore from 'store/store'
import { initialState as userInitialState } from 'store/user/reducer'

import { RootState } from './rootReducer'

export const configureTestStore = (overrideData?: Partial<RootState>) => {
  const initialData = {
    features: { ...featuresInitialState, initialized: true },
    notification: notificationInitialState,
    offers: offersInitialState,
    user: userInitialState,
  }

  return createStore({ ...initialData, ...overrideData }).store
}
