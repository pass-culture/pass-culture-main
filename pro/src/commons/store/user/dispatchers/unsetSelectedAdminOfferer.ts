import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunk } from '../../store'
import { setSelectedAdminOfferer } from '../reducer'

export const unsetSelectedAdminOfferer = (): AppThunk => (dispatch) => {
  dispatch(setSelectedAdminOfferer(null))

  localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
}
