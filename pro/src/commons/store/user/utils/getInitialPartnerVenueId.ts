import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'

/**
 * Compute the initially Partner Space selected venue ID when possible.
 */
export const getInitialPartnerVenueId = (
  venues: VenueListItemResponseModel[],
  newOffererId?: number | undefined
): number | null => {
  // ---------------------------------------------------------------------------
  // Priority 1: If available, get the venue ID from URL params
  //    - id-structure : optional Pro param to ease venue selection and new BO switcher
  //    - venue (deprecated) : old Back Office switcher

  const urlSearchParams = new URLSearchParams(globalThis.location.search)
  let selectedVenueIdFromUrl = Number(urlSearchParams.get('id-structure'))
  if (!selectedVenueIdFromUrl) {
    // TODO(mdesquilbet, 12/11/2026): remove access to deprecated 'venue' param
    // if no sentry error has been raise for some time.
    selectedVenueIdFromUrl = Number(urlSearchParams.get('venue'))
    if (selectedVenueIdFromUrl) {
      const error = new Error(
        "'venue' query param is deprecated and should not be used anymore."
      )
      console.warn(error)
      sendSentryCustomError(error)
    }
  }
  const selectedVenue = venues.filter(
    (venue) => venue.id === selectedVenueIdFromUrl
  )
  if (selectedVenueIdFromUrl && selectedVenue) {
    return selectedVenueIdFromUrl
  }

  // ---------------------------------------------------------------------------
  // Priority 2: If the user associated themselves with a new offerer,
  // get the only offerer venue ID if there is only one,
  // or none if this offerer has multiple venues

  if (newOffererId) {
    const newOffererVenues = venues.filter(
      (venue) => venue.managingOfferer.id === newOffererId
    )

    return newOffererVenues.length === 1 ? newOffererVenues[0].id : null
  }

  // ---------------------------------------------------------------------------
  // Priority 3: If available, get the venue ID from local storage.

  const selectedPartnerVenueIdFromLocalStorage = Number(
    localStorageManager.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)
  )
  if (
    selectedPartnerVenueIdFromLocalStorage &&
    venues.some((venue) => venue.id === selectedPartnerVenueIdFromLocalStorage)
  ) {
    return selectedPartnerVenueIdFromLocalStorage
  }

  // ---------------------------------------------------------------------------
  // Priority 4: If the user has only one venue, we select it.

  const firstVenue = venues[0]
  if (firstVenue && venues.length === 1) {
    return firstVenue.id
  }

  // ---------------------------------------------------------------------------
  // Priority 5: If the user has multiple venues OR no venue at all (registration),
  // the router permissions guard will redirect the user to the approriate page.

  return null
}
