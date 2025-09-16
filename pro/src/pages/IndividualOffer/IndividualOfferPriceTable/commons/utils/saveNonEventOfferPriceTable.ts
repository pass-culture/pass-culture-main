import { mutate } from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'

import type { PriceTableFormValues } from '../schemas'
import { toThingStockCreateBodyModel } from './toThingStockCreateBodyModel'
import { toThingStockUpdateBodyModel } from './toThingStockUpdateBodyModel'

export const saveNonEventOfferPriceTable = async (
  formValues: PriceTableFormValues,
  {
    offer,
  }: {
    offer: GetIndividualOfferWithAddressResponseModel
  }
) => {
  const firstEntry = formValues.entries[0]
  await api.patchOffer(offer.id, { isDuo: formValues.isDuo })
  await mutate([GET_OFFER_QUERY_KEY, offer.id])

  const departementCode = getDepartmentCode(offer)

  if (firstEntry.id) {
    await api.updateThingStock(
      firstEntry.id,
      toThingStockUpdateBodyModel(formValues, { departementCode })
    )
  } else {
    await api.createThingStock(
      toThingStockCreateBodyModel(formValues, { departementCode })
    )
  }
}
