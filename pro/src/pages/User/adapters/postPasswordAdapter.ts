import { api } from 'apiClient/api'
import { ApiError, ChangePasswordBodyModel } from 'apiClient/v1'

type PayloadFailure = Record<string, string>
export type PostPasswordAdapter = Adapter<
  ChangePasswordBodyModel,
  null,
  PayloadFailure
>

const postPasswordAdapter: PostPasswordAdapter = async (
  values: ChangePasswordBodyModel
) => {
  try {
    await api.postChangePassword(values)

    return {
      isOk: true,
      message: '',
      payload: null,
    }
  } catch (error) {
    if (error instanceof ApiError) {
      return {
        isOk: false,
        message: 'Une erreur est présente dans le formulaire',
        payload: error.body,
      }
    }
  }
  return {
    isOk: false,
    message: 'Une erreur est survenue lors de la sauvegarde de vos données',
    payload: null,
  }
}

export default postPasswordAdapter
