import { SharedCurrentUserResponseModel } from '@/apiClient//v1'
import { DeepPartial } from '@/commons/custom_types/utils'
import { OffererState } from '@/commons/store/offerer/reducer'

export const sharedCurrentUserFactory = (
  customSharedCurrentUser: Partial<SharedCurrentUserResponseModel> = {}
): SharedCurrentUserResponseModel => ({
  id: 1,
  firstName: 'John',
  dateCreated: '2022-07-29T12:18:43.087097Z',
  email: 'john@do.net',
  isAdmin: false,
  isEmailValidated: true,
  isImpersonated: false,
  roles: [],
  ...customSharedCurrentUser,
})

export const currentOffererFactory = (
  customOfferer: DeepPartial<OffererState> = {}
): DeepPartial<OffererState> => ({
  offererNames: [...(customOfferer.offererNames ?? [])],
  currentOfferer: {
    id: 1,
    isOnboarded: true,
    ...customOfferer.currentOfferer,
  },
})
