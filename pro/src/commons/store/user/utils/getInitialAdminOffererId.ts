import type {
  GetOffererNameResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

/**
 * Compute the initially Administration Space selected offerer ID when possible.
 */
export const getInitialAdminOffererId = ({
  offererNames,
  selectedPartnerVenue,
}: {
  offererNames: GetOffererNameResponseModel[]
  selectedPartnerVenue: GetVenueResponseModel | null
}): number | null => {
  // ---------------------------------------------------------------------------
  // Priority 1: If available, get the offerer ID from URL params (Back Office switcher).

  const urlSearchParams = new URLSearchParams(globalThis.location.search)
  const selectedOffererIdFromUrl = Number(urlSearchParams.get('offerer'))
  if (selectedOffererIdFromUrl) {
    return selectedOffererIdFromUrl
  }

  // ---------------------------------------------------------------------------
  // Priority 2: If available, get the Administration Space selected offerer ID from the Local Storage.

  const selectedAdminOffererIdFromLocalStorage = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID
  )
  if (selectedAdminOffererIdFromLocalStorage) {
    const selectedOfferer = offererNames.find(
      (offerer) => offerer.id === Number(selectedAdminOffererIdFromLocalStorage)
    )

    if (selectedOfferer) {
      return selectedOfferer.id
    }

    // If there is no matching offerer, we let the next option fall through
    // to gracefully handle local storage inconsistencies.
  }

  // ---------------------------------------------------------------------------
  // Priority 3: If an initial Partner Space selected venue has been computed,
  // use its parent offerer ID as the initial Administration Space selected offerer ID.

  // Deliberately non-DRY for clarity
  const selectedAdminOffererIdFromSelectedPartnerVenue =
    selectedPartnerVenue?.managingOfferer.id
  if (selectedAdminOffererIdFromSelectedPartnerVenue) {
    const selectedOfferer = offererNames.find(
      (offerer) => offerer.id === selectedPartnerVenue.managingOfferer.id
    )

    if (selectedOfferer) {
      return selectedOfferer.id
    } else {
      return null
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 4: Select the first available offerer (sorted by name in Backend)
  // as the initial Administration Space selected offerer ID,
  // Priority 5: or none if there are no offerers at all (= new user signup).

  return offererNames.at(0)?.id ?? null
}
