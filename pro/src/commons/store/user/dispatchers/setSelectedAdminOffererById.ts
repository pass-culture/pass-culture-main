import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetOffererResponseModel } from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleError } from '@/commons/errors/handleError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'
import { setSelectedAdminOfferer } from '../reducer'
import { logout } from './logout'

export const setSelectedAdminOffererById = createAsyncThunk<
  void,
  number | GetOffererResponseModel,
  AppThunkApiConfig
>(
  'user/setSelectedAdminOffererById',
  async (offererOrOffererId, { dispatch }) => {
    try {
      const nextOfferer =
        typeof offererOrOffererId === 'number'
          ? await api.getOfferer(offererOrOffererId)
          : offererOrOffererId
      dispatch(setSelectedAdminOfferer(nextOfferer))
      localStorageManager.setItem(
        LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID,
        String(nextOfferer.id)
      )
    } catch (err) {
      handleError(
        err,
        "Une erreur est survenue lors du chargement de l'entité juridique."
      )
      if (isErrorAPIError(err) || err instanceof FrontendError) {
        logout()
      }
    }
  }
)
