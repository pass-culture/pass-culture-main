import type { VenueListItemLiteResponseModel } from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

/**
 * Compute the initially Partner Space selected venue ID when possible.
 */
export const getInitialPartnerVenueId = (
  venues: VenueListItemLiteResponseModel[],
  newOffererId?: number | undefined
): number | null => {
  // ---------------------------------------------------------------------------
  // Priority 1: If the user associated themselves with a new offerer,
  // get the only offerer venue ID if there is only one,
  // or none if this offerer has multiple venues

  if (newOffererId) {
    const newOffererVenues = venues.filter(
      (venue) => venue.managingOffererId === newOffererId
    )

    return newOffererVenues.length === 1 ? newOffererVenues[0].id : null
  }

  // ---------------------------------------------------------------------------
  // Priority 2: If available, get the venue ID from local storage.

  const selectedVenueIdFromLocalStorage = Number(
    localStorageManager.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)
  )
  if (
    selectedVenueIdFromLocalStorage &&
    venues.some((venue) => venue.id === selectedVenueIdFromLocalStorage)
  ) {
    return selectedVenueIdFromLocalStorage
  }

  // ---------------------------------------------------------------------------
  // Priority 3: If the user has only one venue, we select it.

  const firstVenue = venues.at(0)
  if (firstVenue && venues.length === 1) {
    return firstVenue.id
  }

  // ---------------------------------------------------------------------------
  // Priority 4: If the user has multiple venues OR no venue at all (registration),
  // the router permissions guard will redirect the user to the approriate page.

  return null
}
