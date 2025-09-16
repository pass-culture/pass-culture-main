import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'

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
  await api.patchOffer(offer.id, { isDuo: formValues.isDuo })
  await api.postPriceCategories(offer.id, toPriceCategoryBody(formValues))
  await mutate([GET_OFFER_QUERY_KEY, offer.id])
}
