import { API_URL } from '../../../../utils/config'

export const handleRequestMailingService = async (userInformations) => {
  try {
    const response = await fetch(`${API_URL}/users/current/mailing_contacts`, {
      body: JSON.stringify(userInformations),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'POST',
    })

    // if (response.status === 200) {
    //   return true
    // } else {
    //   return await response.json()
    // }
    return true
  } catch (error) {
    throw new Error(error)
  }
}
