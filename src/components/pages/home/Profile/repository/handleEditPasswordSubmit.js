import { API_URL } from '../../../../../utils/config'

export const handleEditPasswordSubmit = async (
  formValues,
  handleSubmitFail,
  handleSubmitSuccess
) => {
  try {
    const response = await fetch(`${API_URL}/users/current/change-password`, {
      body: JSON.stringify(formValues),
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      method: 'POST',
    })

    if (response.status === 400) {
      handleSubmitFail(await response.json())
    } else if (response.ok === false) {
      throw new Error(`Status: ${response.status}, Status text: ${response.statusText}`)
    } else {
      handleSubmitSuccess()
    }
  } catch (error) {
    throw new Error(error)
  }
}
