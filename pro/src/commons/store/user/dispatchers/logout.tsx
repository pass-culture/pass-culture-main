import { createAsyncThunk } from '@reduxjs/toolkit'

import { api } from '@/apiClient/api'

import {
  SAVED_OFFERER_ID_KEY,
  SAVED_VENUE_ID_KEY,
} from '../../../core/shared/constants'
import { handleError } from '../../../errors/handleError'
import { storageAvailable } from '../../../utils/storageAvailable'
import { updateCurrentOfferer, updateOffererNames } from '../../offerer/reducer'
import type { AppThunkApiConfig } from '../../store'
import {
  setSelectedVenue,
  setVenues,
  updateUser,
  updateUserAccess,
} from '../reducer'

export const logout = createAsyncThunk<void, void, AppThunkApiConfig>(
  'user/logout',
  async (_, { dispatch }) => {
    try {
      await api.signout()
    } catch (err) {
      handleError(err, 'Une erreur est survenue lors de la déconnexion.')
    }

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
)
