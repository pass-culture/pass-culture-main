import { api } from 'apiClient/api'
import {
  ApiError,
  UserPhoneBodyModel,
  UserPhoneResponseModel,
} from 'apiClient/v1'

type IPayloadFailure = Record<string, string>
export type PatchPhoneAdapter = Adapter<
  UserPhoneBodyModel,
  UserPhoneResponseModel,
  IPayloadFailure
>

const patchPhoneAdapter: PatchPhoneAdapter = async (
  values: UserPhoneBodyModel
) => {
  try {
    const payload = await api.patchUserPhone(values)

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

export default patchPhoneAdapter
