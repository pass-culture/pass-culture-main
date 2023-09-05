import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

type Params = {
  offererId: number
  email: string
}

type GetInviteMemberAdapter = Adapter<Params, null, null>

const postInviteMemberAdapter: GetInviteMemberAdapter = async ({
  offererId,
  email,
}) => {
  try {
    await api.inviteMember(offererId, { email: email })

    return {
      isOk: true,
      message: "L'invitation a bien été envoyée.",
      payload: null,
    }
  } catch (error) {
    let message = "Une erreur est survenue lors de l'envoi de l'invitation."
    if (isErrorAPIError(error) && error.status == 400 && error.body.email) {
      message = error.body.email
    }
    return {
      isOk: false,
      message: message,
      payload: null,
    }
  }
}

export default postInviteMemberAdapter
