import { API_URL } from '../../../utils/config'

const CURRENT_USER_PATH = `${API_URL}/beneficiaries/current`

export async function getCurrentUser() {
  const response = await fetch(CURRENT_USER_PATH, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (response.status !== 200) return null

  return await response.json()
}

export async function patchCurrentUser(payload) {
  const response = await fetch(CURRENT_USER_PATH, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    method: 'PATCH',
  })

  if (response.status !== 200) {
    if ('json' in response) throw await response.json()
    throw new Error('Error patching currentUser')
  }

  return await response.json()
}
