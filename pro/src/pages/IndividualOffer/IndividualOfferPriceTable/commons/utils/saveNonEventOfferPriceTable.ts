import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  GET_OFFER_QUERY_KEY,
  GET_STOCKS_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'

import type { PriceTableFormValues } from '../schemas'
import { toThingStocksBulkUpsertBodyModel } from './toThingStocksBulkUpsertBodyModel'

export const saveNonEventOfferPriceTable = async (
  formValues: PriceTableFormValues,
  {
    offer,
  }: {
    offer: GetIndividualOfferWithAddressResponseModel
  }
) => {
  await mutate(
    [GET_OFFER_QUERY_KEY, offer.id],
    api.patchOffer(offer.id, { isDuo: formValues.isDuo }),
    {
      revalidate: false,
    }
  )

  const departementCode = getDepartmentCode(offer)

  await api.upsertOfferStocks(
    offer.id,
    toThingStocksBulkUpsertBodyModel(formValues, { departementCode })
  )
  await mutate([GET_STOCKS_QUERY_KEY, offer.id])
}
