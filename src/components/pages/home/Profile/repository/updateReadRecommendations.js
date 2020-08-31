import { API_URL } from '../../../../../utils/config'

export const updateReadRecommendations = async readRecommendations => {
  try {
    const response = await fetch(`${API_URL}/recommendations/read`, {
      body: JSON.stringify(readRecommendations),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'PUT',
    })

    if (response.ok === false) {
      throw Error(`Status: ${response.status}, Status text: ${response.statusText}`)
    }
  } catch (error) {
    throw new Error(error)
  }
}
