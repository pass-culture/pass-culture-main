import { createAsyncThunk } from '@reduxjs/toolkit'

import { handleError } from '@/commons/errors/handleError'
import { API_URL } from '@/commons/utils/config'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

import type { AppThunkApiConfig } from '../../store'

// This dispatcher is useless for now since it doesn't use Redux (anymore) but we plan to do it once both below tasks are done.
// TODO (igabriele, 2025-11-21): 1. We should investigate why Redux store updates are not applied in orderly fashion (from AppRouterGuard to page and not the order way around).
// TODO (igabriele, 2025-11-21): 2. To avoid all this reload shenanigans, we should migrate to a JWT-based authentication system (so ONLY Frontend handle auth and permission instead of sharing responsability in a messy way)
export const logout = createAsyncThunk<void, void, AppThunkApiConfig>(
  'user/logout',
  async (_) => {
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)

    try {
      // we use fetch directly to avoid a circular import with request.ts
      await fetch(`${API_URL}/users/signout`, {
        credentials: 'include',
      })
      window.location.reload()
    } catch (err) {
      handleError(err, 'Une erreur est survenue lors de la déconnexion.')
      window.location.href = '/connexion'
    }
  }
)
