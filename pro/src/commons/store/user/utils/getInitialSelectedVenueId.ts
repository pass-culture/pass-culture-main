import type { VenueListItemResponseModel } from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

/**
 * Determine the initially selected venue ID when possible.
 *
 * The selected venue ID only applies to the partner space (and not the administration one).
 */
export const getInitialSelectedVenueId = (
  venues: VenueListItemResponseModel[]
): number | null => {
  // ---------------------------------------------------------------------------
  // Priority 1: If available, get the venue ID from local storage.

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
  // Priority 2: If the user has only one venue, we select it.

  const firstVenue = venues.at(0)
  if (firstVenue && venues.length === 1) {
    return firstVenue.id
  }

  // ---------------------------------------------------------------------------
  // Priority 3: If the user has multiple venues OR no venue at all (registration),
  // the router permissions guard will redirect the user to the approriate page.

  return null
}
