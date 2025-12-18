import type {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

// TODO (igabriele, 2026-01-08): Delete this util once `WIP_SWITCH_VENUE` is enabled in production.
export const getInitialOffererIdAndVenueId = (
  offerersNames: GetOffererNameResponseModel[],
  venues: VenueListItemResponseModel[]
): {
  initialOffererId: number | null
  initialVenueId: number | null
} => {
  // ---------------------------------------------------------------------------
  // Priority 1: If available, get the offerer ID from URL params (Back Office switcher).
  // TODO (igabriele, 2025-10-28): Handle that case properly before `WIP_SWITCH_VENUE` is enabled in production.

  const urlSearchParams = new URLSearchParams(window.location.search)
  const selectedOffererIdFromUrl = Number(urlSearchParams.get('structure'))
  if (selectedOffererIdFromUrl) {
    return {
      initialOffererId: selectedOffererIdFromUrl,
      initialVenueId: null,
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 2: If available, get the venue ID from local storage (since the offerer will entirely disappear from Frontend).

  const selectedVenueIdFromLocalStorage = Number(
    localStorageManager.getItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)
  )
  if (
    selectedVenueIdFromLocalStorage &&
    venues.some((venue) => venue.id === selectedVenueIdFromLocalStorage)
  ) {
    return {
      initialOffererId: null,
      initialVenueId: selectedVenueIdFromLocalStorage,
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 3: If available, get the offerer ID from local storage (legacy behavior fallback).
  // TODO (igabriele, 2025-10-28): Delete this section once `WIP_SWITCH_VENUE` is enabled in production.

  const selectedOffererIdFromLocalStorage = Number(
    localStorageManager.getItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
  )
  if (
    selectedOffererIdFromLocalStorage &&
    offerersNames.some(
      (offerer) => offerer.id === selectedOffererIdFromLocalStorage
    )
  ) {
    return {
      initialOffererId: selectedOffererIdFromLocalStorage,
      initialVenueId: null,
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 4: If there are venues in the store (= from the API), we get the first active venue.

  const firstVenue = venues.at(0)
  if (firstVenue) {
    return {
      initialOffererId: null,
      initialVenueId: firstVenue.id,
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 5: We get the first available offerer because there are no venues at all (legacy behavior fallback),
  // Priority 6: or none if there are no offerers at all (= new user signup).
  // TODO (igabriele, 2025-10-28): Handle that case properly before `WIP_SWITCH_VENUE` is enabled in production.
  // TODO (igabriele, 2025-10-28): Delete this section once `WIP_SWITCH_VENUE` is enabled in production.
  const firstOffererName = offerersNames.at(0)
  return {
    initialOffererId: firstOffererName?.id ? Number(firstOffererName.id) : null,
    initialVenueId: null,
  }
}
