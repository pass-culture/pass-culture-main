import { API_URL } from '../../../utils/config'

export async function getCurrentUser() {
  const response = await fetch(`${API_URL}/beneficiaries/current`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (response.status != 200) return null

  return await response.json()
}

export async function patchCurrentUser(payload) {
  const response = await fetch(`${API_URL}/users/current`, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
    method: 'PATCH',
  })

  if (response.status != 200) {
    if ('json' in response) throw await response.json()
    throw new Error('Error patching currentUser')
  }

  return await response.json()
}
