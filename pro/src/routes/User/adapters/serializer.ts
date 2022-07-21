import { IUseCurrentUserReturn } from 'components/hooks/useCurrentUser'
import { UserIdentityResponseModel } from 'apiClient/v1'

export const serializeUser = (
  user: IUseCurrentUserReturn
): UserIdentityResponseModel => {
  const currentUser = user.currentUser
  return {
    firstName: currentUser.firstName || '',
    lastName: currentUser.lastName || '',
  }
}
