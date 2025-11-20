import { createAsyncThunk } from '@reduxjs/toolkit'
import { batch } from 'react-redux'

import { api } from '@/apiClient/api'
import { handleError } from '@/commons/errors/handleError'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import {
  setCurrentOffererName,
  updateCurrentOfferer,
  updateOffererNames,
} from '../../offerer/reducer'
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

    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)

    console.log('logout')

    // TODO: we should investigate problem of state concurrency
    // causing problem during logout
    // batch(
    // ;(() => {
    dispatch(updateOffererNames(null))
    dispatch(updateCurrentOfferer(null))
    dispatch(setCurrentOffererName(null))
    dispatch(setVenues(null))
    dispatch(setSelectedVenue(null))
    dispatch(updateUser(null))
    dispatch(updateUserAccess(null))
    // })()
  }
)
