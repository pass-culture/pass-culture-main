import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export const venueSubmitRedirectUrl = (
  isCreatingVenue: boolean,
  offererId: number,
  currentUser: SharedCurrentUserResponseModel
) => {
  return currentUser.isAdmin
    ? `/structures/${offererId}`
    : `${isCreatingVenue ? '/accueil?success' : '/accueil'}`
}
