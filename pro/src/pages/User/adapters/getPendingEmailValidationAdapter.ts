import { api } from 'apiClient/api'
import { ApiError, UserEmailValidationResponseModel } from 'apiClient/v1'

type PayloadFailure = Record<string, string>
type GetPendingEmailValidationAdapter = Adapter<
  void,
  UserEmailValidationResponseModel,
  PayloadFailure
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
      message: 'Une erreur est survenue au chargement du formulaire',
      payload: null,
    }
  }
