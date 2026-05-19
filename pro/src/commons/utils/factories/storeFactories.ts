import type { SharedCurrentUserResponseModel } from '@/apiClient/v1'

import type { UserSliceState } from '../../store/user/reducer'

export const makeUserSliceState = (
  overrides: Partial<UserSliceState> = {}
): UserSliceState => ({
  currentUser: null,
  offererNames: null,
  offererNamesValidated: null,
  offerersNamesWithPendingValidation: null,
  selectedAdminOfferer: null,
  selectedPartnerVenue: null,
  venues: null,
  venuesWithPendingValidation: null,
  ...overrides,
})

export const sharedCurrentUserFactory = (
  customSharedCurrentUser: Partial<SharedCurrentUserResponseModel> = {}
): SharedCurrentUserResponseModel => ({
  id: 1,
  firstName: 'John',
  dateCreated: '2022-07-29T12:18:43.087097Z',
  email: 'john@do.net',
  isEmailValidated: true,
  isImpersonated: false,
  roles: [],
  ...customSharedCurrentUser,
})
