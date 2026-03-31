import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunk } from '../../store'
import { setSelectedPartnerVenue } from '../reducer'

export const unsetSelectedPartnerVenue = (): AppThunk => (dispatch) => {
  dispatch(setSelectedPartnerVenue(null))

  localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)
}
