import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { PriceCategoryBody } from 'apiClient/v1'

type TSuccessPayload = Record<string, unknown>
type TFailurePayload = { errors: Record<string, string>[] }
type PostPriceCategoriesAdapter = Adapter<
  {
    offerId: number
    requestBody?: PriceCategoryBody
  },
  TSuccessPayload,
  TFailurePayload
>

const postPriceCategoriesAdapter: PostPriceCategoriesAdapter = async ({
  offerId,
  requestBody,
}) => {
  try {
    await api.postPriceCategories(offerId, requestBody)
    return {
      isOk: true,
      message: 'Vos modifications ont bien été prises en compte',
      payload: {},
    }
  } catch (error) {
    let formErrors = []
    /* istanbul ignore next */
    if (isErrorAPIError(error)) {
      formErrors = error.body
    }

    return {
      isOk: false,
      message: 'Une erreur est survenue lors de la mise à jour de votre tarif',
      payload: {
        errors: formErrors,
      },
    }
  }
}
export default postPriceCategoriesAdapter
