import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'
import { updateAdminCurrentOfferer } from '../reducer'

export const setAdminCurrentOfferer = createAsyncThunk<
  void,
  number | null,
  AppThunkApiConfig
>('offerer/setAdminCurrentOfferer', async (offererId, { dispatch }) => {
  if (offererId === null) {
    dispatch(updateAdminCurrentOfferer(null))
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
    return
  }

  try {
    const offerer = await api.getOfferer(offererId)
    dispatch(updateAdminCurrentOfferer(offerer))
    localStorageManager.setItem(
      LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID,
      String(offererId)
    )
  } catch {
    dispatch(updateAdminCurrentOfferer(null))
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID)
  }
})
