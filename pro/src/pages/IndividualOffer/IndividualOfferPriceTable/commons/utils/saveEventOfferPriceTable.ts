import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { handleError } from '@/commons/errors/handleError'

import { FAILED_PATCH_OFFER_USER_MESSAGE } from '../constants'
import type { PriceTableFormValues } from '../schemas'
import { toPriceCategoryBody } from './toPriceCategoryBody'

export const saveEventOfferPriceTable = async (
  formValues: PriceTableFormValues,
  {
    offer,
  }: {
    offer: GetIndividualOfferWithAddressResponseModel
  }
) => {
  try {
    await api.patchOffer(offer.id, { isDuo: formValues.isDuo })

    await api.postPriceCategories(offer.id, toPriceCategoryBody(formValues))
  } catch (error) {
    return handleError(error, FAILED_PATCH_OFFER_USER_MESSAGE)
  }
}
