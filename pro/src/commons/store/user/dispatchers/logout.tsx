import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '../../../core/shared/constants'
import { storageAvailable } from '../../../utils/storageAvailable'
import { updateCurrentOfferer, updateOffererNames } from '../../offerer/reducer'
import type { AppThunk } from '../../store'
import {
  setSelectedVenue,
  setVenues,
  updateUser,
  updateUserAccess,
} from '../reducer'

export const logout = (): AppThunk => (dispatch) => {
  if (storageAvailable('localStorage')) {
    localStorage.removeItem(SAVED_OFFERER_ID_KEY)
    localStorage.removeItem(SAVED_VENUE_ID_KEY)
  }

  dispatch(updateOffererNames(null))
  dispatch(updateCurrentOfferer(null))
  dispatch(setVenues(null))
  dispatch(setSelectedVenue(null))
  dispatch(updateUser(null))
  dispatch(updateUserAccess(null))
}
