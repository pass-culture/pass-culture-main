import type { UseFormReturn } from 'react-hook-form'
import { mutate } from 'swr'

import { apiNew } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1/new'
import {
  GET_OFFER_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'

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
      apiNew.patchOffer({
        path: { offer_id: offer.id },
        // TODO (rchaffal) to remove once PatchOfferBodyModel is migrated to Pydantic V2
        // @ts-expect-error
        body: { isDuo: formValues.isDuo },
      }),
      { revalidate: false }
    )
  }
  if (dirtyFields) {
    await mutate(
      [GET_OFFER_QUERY_KEY, offer.id],
      apiNew.replaceOfferPriceCategories({
        path: { offer_id: offer.id },
        body: toPriceCategoryBody(formValues),
      }),
      { revalidate: false }
    )
    await mutate([GET_STOCKS_QUERY_KEY, offer.id])
  }
}
