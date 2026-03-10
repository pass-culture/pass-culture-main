import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { HTTP_STATUS, isErrorAPIError } from '@/apiClient/helpers'
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
  {
    offererId: number | GetOffererResponseModel
    offererNamesAttachedIds?: number[]
  },
  AppThunkApiConfig
>(
  'user/setSelectedAdminOffererById',
  async (
    { offererId: offererOrOffererId, offererNamesAttachedIds = [] },
    { dispatch }
  ) => {
    try {
      const offererId =
        typeof offererOrOffererId === 'number'
          ? offererOrOffererId
          : offererOrOffererId.id

      if (
        offererNamesAttachedIds.length > 0 &&
        !offererNamesAttachedIds.includes(offererId)
      ) {
        // if the offerer is unattached, we set a minimal offerer to avoid having getOfferer() return a 403
        // this allows to display the unattached banner to the user
        const minimalOfferer = {
          id: offererId,
        } as GetOffererResponseModel
        dispatch(setSelectedAdminOfferer(minimalOfferer))
        localStorageManager.setItem(
          LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID,
          String(offererId)
        )
        return
      }

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
      if (isErrorAPIError(err) && err.status === HTTP_STATUS.FORBIDDEN) {
        const offererId =
          typeof offererOrOffererId === 'number'
            ? offererOrOffererId
            : offererOrOffererId.id

        const minimalOfferer = {
          id: offererId,
        } as GetOffererResponseModel
        dispatch(setSelectedAdminOfferer(minimalOfferer))
        localStorageManager.setItem(
          LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID,
          String(offererId)
        )
        return
      }

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
