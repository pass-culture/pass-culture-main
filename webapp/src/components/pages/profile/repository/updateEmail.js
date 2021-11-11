import { API_URL } from '../../../../utils/config'

export const updateEmail = async ({ new_email, password }) => {
  return fetch(`${API_URL}/beneficiaries/change_email_request`, {
    body: JSON.stringify({ new_email, password }),
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    method: 'PUT',
  })
}

export default updateEmail
