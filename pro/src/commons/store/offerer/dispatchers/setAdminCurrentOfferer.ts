import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'
import { updateAdminCurrentOfferer } from '../reducer'

export const setAdminCurrentOfferer = createAsyncThunk<
  void,
  { offererId: number; offerer?: GetOffererResponseModel | null },
  AppThunkApiConfig
>(
  'offerer/setAdminCurrentOfferer',
  async ({ offererId, offerer }, { dispatch }) => {
    try {
      let offererToSet = offerer ?? null
      if (!offererToSet) {
        offererToSet = await api.getOfferer(offererId)
      }
      dispatch(updateAdminCurrentOfferer(offererToSet))
      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID,
        String(offererId)
      )
    } catch {
      dispatch(updateAdminCurrentOfferer(null))
      localStorageManager.removeItem(
        LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID
      )
    }
  }
)
