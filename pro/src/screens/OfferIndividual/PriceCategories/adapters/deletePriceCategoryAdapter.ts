import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

type SuccessPayload = Record<string, unknown>
type FailurePayload = { errors: Record<string, string>[] }
type DeletePriceCategoryAdapter = Adapter<
  {
    offerId: number
    priceCategoryId: number
  },
  SuccessPayload,
  FailurePayload
>

const deletePriceCategoryAdapter: DeletePriceCategoryAdapter = async ({
  offerId,
  priceCategoryId,
}) => {
  try {
    await api.deletePriceCategory(offerId, priceCategoryId)
    return {
      isOk: true,
      message: 'Le tarif a été supprimé.',
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
      message: 'Une erreur est survenue lors de la suppression de votre tarif',
      payload: {
        errors: formErrors,
      },
    }
  }
}
export default deletePriceCategoryAdapter
