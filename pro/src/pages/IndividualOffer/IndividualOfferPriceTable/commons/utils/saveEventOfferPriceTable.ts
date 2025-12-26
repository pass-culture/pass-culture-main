import type { UseFormReturn } from 'react-hook-form'
import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'

import type { PriceTableFormValues } from '../schemas'
import { toPriceCategoryBody } from './toPriceCategoryBody'

export const saveEventOfferPriceTable = async (
  formValues: PriceTableFormValues,
  form: UseFormReturn<PriceTableFormValues>,
  {
    offer,
  }: {
    offer: GetIndividualOfferWithAddressResponseModel
  }
) => {
  const { dirtyFields } = form.formState
  if (dirtyFields.isDuo) {
    await mutate(
      [GET_OFFER_QUERY_KEY, offer.id],
      api.patchOffer(offer.id, { isDuo: formValues.isDuo }),
      { revalidate: false }
    )
  }
  if (dirtyFields) {
    await mutate(
      [GET_OFFER_QUERY_KEY, offer.id],
      api.replaceOfferPriceCategories(
        offer.id,
        toPriceCategoryBody(formValues)
      ),
      { revalidate: false }
    )
  }
}
