import { FeatureResponseModel, UserRole } from 'apiClient/v1'
import createStore from 'store'
import { initialState as featuresInitialState } from 'store/features/reducer'
import { initialState as offersInitialState } from 'store/offers/reducer'
import { initialState as maintenanceInitialState } from 'store/reducers/maintenanceReducer'
import { initialState as notificationInitialState } from 'store/reducers/notificationReducer'
import { initialState as userInitialState } from 'store/user/reducer'

import { RootState } from './reducers'

export const configureTestStore = (overrideData?: Partial<RootState>) => {
  const initialData = {
    features: { ...featuresInitialState, initialized: true },
    maintenance: maintenanceInitialState,
    notification: notificationInitialState,
    offers: offersInitialState,
    user: userInitialState,
  }

  return createStore({ ...initialData, ...overrideData }).store
}

export const baseStoreFactory = ({
  isAdmin = false,
  featureList = [],
}: Partial<{
  isAdmin: boolean
  featureList: string[]
}> = {}): Partial<RootState> => {
  const featuresList: FeatureResponseModel[] = featureList.map(featureName => ({
    id: featureName,
    isActive: true,
    description: '',
    name: featureName,
    nameKey: featureName,
  }))

  return {
    user: {
      initialized: true,
      currentUser: {
        id: 1,
        email: 'email@example.com',
        isAdmin: isAdmin,
        roles: isAdmin ? [UserRole.ADMIN] : [UserRole.PRO],
        isEmailValidated: true,
        dateCreated: '2022-07-29T12:18:43.087097Z',
      },
    },
    features: {
      initialized: true,
      list: featuresList,
    },
  }
}
