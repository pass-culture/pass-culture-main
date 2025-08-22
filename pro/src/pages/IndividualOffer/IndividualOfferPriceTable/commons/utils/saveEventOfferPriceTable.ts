import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'

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
  } catch {
    throw new FrontendError(
      'Une erreur est survenue lors de la mise à jour de votre tarif'
    )
  }

  try {
    await api.postPriceCategories(offer.id, toPriceCategoryBody(formValues))
  } catch {
    throw new FrontendError(
      'Une erreur est survenue lors de la mise à jour de votre tarif'
    )
  }
}
