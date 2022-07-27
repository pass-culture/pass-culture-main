import {
  SharedCurrentUserResponseModel,
  UserIdentityResponseModel,
} from 'apiClient/v1'

export const serializeUserIdentity = (
  user: SharedCurrentUserResponseModel
): UserIdentityResponseModel => {
  return {
    firstName: user.firstName || '',
    lastName: user.lastName || '',
  }
}
