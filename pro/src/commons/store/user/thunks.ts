import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type {
  GetOffererNameResponseModel,
  SharedCurrentUserResponseModel,
} from '@/apiClient/v1'
import { SAVED_OFFERER_ID_KEY } from '@/commons/core/shared/constants'
import {
  updateCurrentOfferer,
  updateOffererNames,
} from '@/commons/store/offerer/reducer'
import { updateUser, updateUserAccess } from '@/commons/store/user/reducer'
import { storageAvailable } from '@/commons/utils/storageAvailable'

export const initializeUserThunk = createAsyncThunk(
  'user/initialize',
  async (
    user: SharedCurrentUserResponseModel,
    { dispatch, rejectWithValue }
  ) => {
    try {
      const initializeOfferer = async (
        offererId: number,
        offerersNames: GetOffererNameResponseModel[]
      ) => {
        try {
          const response = await api.getOfferer(offererId)
          dispatch(updateCurrentOfferer(response))
          dispatch(
            updateUserAccess(
              offerersNames
                ? response.isOnboarded
                  ? 'full'
                  : 'no-onboarding'
                : 'no-offerer'
            )
          )
        } catch (e: unknown) {
          if (isErrorAPIError(e) && e.status === 403) {
            // Do nothing at this point,
            // Because a 403 means that the user is waiting for a "rattachement" to the offerer,
            // But we must let him sign in
            dispatch(updateUserAccess('unattached'))

            return
          }
          // Else it's another error we should handle here at sign in
          throw e
        }
      }

      const offerers = await api.listOfferersNames()
      const firstOffererId = offerers.offerersNames[0]?.id

      if (firstOffererId) {
        dispatch(updateOffererNames(offerers.offerersNames))

        if (storageAvailable('localStorage')) {
          const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
          await initializeOfferer(
            savedOffererId ? Number(savedOffererId) : firstOffererId,
            offerers.offerersNames
          )
        } else {
          await initializeOfferer(firstOffererId, offerers.offerersNames)
        }
      } else {
        dispatch(updateUserAccess('no-offerer'))
      }

      dispatch(updateUser(user))

      return { success: true }
    } catch (error: unknown) {
      // In case of error, cancel all state modifications
      dispatch(updateOffererNames(null))
      dispatch(updateCurrentOfferer(null))
      dispatch(updateUser(null))

      if (isErrorAPIError(error)) {
        return rejectWithValue({
          error: 'API_ERROR',
          status: error.status,
          body: error.message,
        })
      }

      return rejectWithValue({ error: 'UNKNOWN_ERROR' })
    }
  }
)
