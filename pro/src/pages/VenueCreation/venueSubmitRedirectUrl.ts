import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export const venueSubmitRedirectUrl = (
  offererId: number,
  currentUser: SharedCurrentUserResponseModel
) => {
  return currentUser.isAdmin ? `/structures/${offererId}` : '/accueil?success'
}
