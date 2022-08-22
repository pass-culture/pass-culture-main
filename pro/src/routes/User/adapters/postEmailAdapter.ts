import { api } from 'apiClient/api'
import { ApiError, UserResetEmailBodyModel } from 'apiClient/v1'

type IPayloadFailure = Record<string, string>
export type PostEmailAdapter = Adapter<
  UserResetEmailBodyModel,
  void,
  IPayloadFailure
>

const postEmailAdapter: PostEmailAdapter = async (
  values: UserResetEmailBodyModel
) => {
  try {
    const payload = await api.postUserEmail(values)

    return {
      isOk: true,
      message: '',
      payload: payload,
    }
  } catch (error) {
    if (error instanceof ApiError)
      return {
        isOk: false,
        message: 'Une erreur est présente dans le formulaire',
        payload: error.body,
      }
  }
  return {
    isOk: false,
    message: 'Une erreur est survenue lors de la sauvegarde de vos données',
    payload: null,
  }
}

export default postEmailAdapter
