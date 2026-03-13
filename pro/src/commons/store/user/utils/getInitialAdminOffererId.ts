import type {
  GetOffererNameResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

/**
 * Compute the initially Administration Space selected offerer ID when possible.
 */
export const getInitialAdminOffererId = ({
  offererNamesAttached,
  selectedVenue,
}: {
  offererNamesAttached: GetOffererNameResponseModel[]
  selectedVenue: GetVenueResponseModel | null
}): number | null => {
  // ---------------------------------------------------------------------------
  // Priority 1: If available, get the Administration Space selected offerer ID from the Local Storage.

  const selectedAdminOffererIdFromLocalStorage = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID
  )
  if (selectedAdminOffererIdFromLocalStorage) {
    const selectedOfferer = offererNamesAttached.find(
      (offerer) => offerer.id === Number(selectedAdminOffererIdFromLocalStorage)
    )

    if (selectedOfferer) {
      return selectedOfferer.id
    } else {
      handleUnexpectedError(
        new FrontendError('`selectedOfferer` is undefined.'),
        {
          // This is not a necessarily a critical issue for the user experience
          // but we need to log it because this is a bug if it happens
          isSilent: true,
        }
      )

      return null
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 2: If an initial Partner Space selected venue has been computed,
  // use its parent offerer ID as the initial Administration Space selected offerer ID.

  // Deliberately non-DRY for clarity
  const selectedAdminOffererIdFromSelectedVenue =
    selectedVenue?.managingOfferer.id
  if (selectedAdminOffererIdFromSelectedVenue) {
    const selectedOfferer = offererNamesAttached.find(
      (offerer) => offerer.id === selectedVenue.managingOfferer.id
    )

    if (selectedOfferer) {
      return selectedOfferer.id
    } else {
      handleUnexpectedError(
        new FrontendError('`selectedOfferer` is undefined.'),
        {
          // This is not a necessarily a critical issue for the user experience
          // but we need to log it because this is a bug if it happens
          isSilent: true,
        }
      )

      return null
    }
  }

  // ---------------------------------------------------------------------------
  // Priority 3: Select the first available offerer (sorted by name in Backend)
  // as the initial Administration Space selected offerer ID,
  // Priority 4: or none if there are no offerers at all (= new user signup).

  return offererNamesAttached.at(0)?.id ?? null
}
