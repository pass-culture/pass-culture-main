import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export const sharedCurrentUserFactory = (
  customSharedCurrentUser: Partial<SharedCurrentUserResponseModel> = {}
): SharedCurrentUserResponseModel => ({
  id: 1,
  firstName: 'John',
  dateCreated: '2022-07-29T12:18:43.087097Z',
  email: 'john@do.net',
  isAdmin: false,
  isEmailValidated: true,
  roles: [],
  ...customSharedCurrentUser,
})
