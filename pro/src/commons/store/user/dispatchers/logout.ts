import { handleError } from '@/commons/errors/handleError'
import { API_URL } from '@/commons/utils/config'
import { localStorageManager } from '@/commons/utils/localStorageManager'

export const logout = async (redirect = true) => {
  localStorageManager.clearPassCultureKeys()

  try {
    // we use fetch directly to avoid a circular import with request.ts
    await fetch(`${API_URL}/users/signout`, {
      credentials: 'include',
    })
  } catch (err) {
    handleError(err, 'Une erreur est survenue lors de la déconnexion.')
  } finally {
    if (redirect) {
      window.location.href = '/connexion'
    }
  }
}
