import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'

type TSuccessPayload = Record<string, unknown>
type TFailurePayload = { errors: Record<string, string>[] }
export type TDeletePriceCategoryAdapter = Adapter<
  {
    offerId: string
    priceCategoryId: string
  },
  TSuccessPayload,
  TFailurePayload
>

const deletePriceCategoryAdapter: TDeletePriceCategoryAdapter = async ({
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
