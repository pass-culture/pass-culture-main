import { API_URL } from '../../../../utils/config'

export const signOut = async () => {
  try {
    const response = await fetch(`${API_URL}/users/signout`, {
      credentials: 'include',
    })

    if (response.ok === false) {
      throw Error(`Status: ${response.status}, Status text: ${response.statusText}`)
    }
  } catch (error) {
    throw new Error(error)
  }
}
