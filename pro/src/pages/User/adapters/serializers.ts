import {
  SharedCurrentUserResponseModel,
  UserPhoneBodyModel,
} from 'apiClient/v1'
import { UserIdentityFormValues } from 'components/UserIdentityForm/types'

export const serializeUserIdentity = (
  user: SharedCurrentUserResponseModel
): UserIdentityFormValues => {
  return {
    firstName: user.firstName || '',
    lastName: user.lastName || '',
  }
}

export const serializeUserPhone = (
  user: SharedCurrentUserResponseModel
): UserPhoneBodyModel => {
  return {
    phoneNumber: user.phoneNumber || '',
  }
}

export const serializeUserEmail = (user: SharedCurrentUserResponseModel) => {
  return {
    email: user.email,
  }
}
