import { handleError } from '@/commons/errors/handleError'
import { API_URL } from '@/commons/utils/config'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export const logout = async () => {
  localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_OFFERER_ID)
  localStorageManager.removeItem(LOCAL_STORAGE_KEY.SELECTED_VENUE_ID)

  try {
    // we use fetch directly to avoid a circular import with request.ts
    await fetch(`${API_URL}/users/signout`, {
      credentials: 'include',
    })
  } catch (err) {
    handleError(err, 'Une erreur est survenue lors de la déconnexion.')
  } finally {
    window.location.href = '/connexion'
  }
}
