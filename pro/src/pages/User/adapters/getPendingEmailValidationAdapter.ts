import { api } from 'apiClient/api'
import { ApiError, UserEmailValidationResponseModel } from 'apiClient/v1'

type IPayloadFailure = Record<string, string>
export type GetPendingEmailValidationAdapter = Adapter<
  void,
  UserEmailValidationResponseModel,
  IPayloadFailure
>

export const getPendingEmailValidationAdapter: GetPendingEmailValidationAdapter =
  async () => {
    try {
      const result = await api.getUserEmailPendingValidation()

      return {
        isOk: true,
        message: null,
        payload: result,
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
      message: 'Une erreur est survenue au chargement du formulaire',
      payload: null,
    }
  }
