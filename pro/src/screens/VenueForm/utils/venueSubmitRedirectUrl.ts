import { SharedCurrentUserResponseModel } from 'apiClient/v1'

export const venueSubmitRedirectUrl = (
  hasNewOfferCreationJourney: boolean,
  isCreatingVenue: boolean,
  offererId: number,
  venueId: number | undefined,
  currentUser: SharedCurrentUserResponseModel
) => {
  let venuesUrl
  if (hasNewOfferCreationJourney) {
    venuesUrl = currentUser.isAdmin
      ? `/structures/${offererId}`
      : `${
          hasNewOfferCreationJourney && isCreatingVenue
            ? '/accueil?success'
            : '/accueil'
        }`
  } else {
    venuesUrl = isCreatingVenue
      ? `/structures/${offererId}/lieux/${venueId}`
      : currentUser.isAdmin
      ? `/structures/${offererId}`
      : '/accueil'
  }
  return venuesUrl
}
