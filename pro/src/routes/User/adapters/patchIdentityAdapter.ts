import { api } from 'apiClient/api'
import {
  ApiError,
  UserIdentityBodyModel,
  UserIdentityResponseModel,
} from 'apiClient/v1'

type IPayloadFailure = Record<string, string>
export type PatchIdentityAdapter = Adapter<
  UserIdentityBodyModel,
  UserIdentityResponseModel,
  IPayloadFailure
>

const patchIdentityAdapter: PatchIdentityAdapter = async (
  values: UserIdentityBodyModel
) => {
  try {
    const payload = await api.patchUserIdentity(values)

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

export default patchIdentityAdapter
