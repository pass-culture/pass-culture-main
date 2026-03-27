import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunk } from '../../store'
import { setSelectedVenue } from '../reducer'

export const unsetSelectedPartnerVenue = (): AppThunk => (dispatch) => {
  dispatch(setSelectedVenue(null))

  localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)
}
