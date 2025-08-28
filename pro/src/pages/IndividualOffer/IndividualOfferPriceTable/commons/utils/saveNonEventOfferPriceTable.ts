import type { UseFormSetError } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { handleError } from '@/commons/errors/handleError'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'

import { FAILED_PATCH_OFFER_USER_MESSAGE } from '../constants'
import type { PriceTableFormValues } from '../schemas'
import { toThingStockCreateBodyModel } from './toThingStockCreateBodyModel'
import { toThingStockUpdateBodyModel } from './toThingStockUpdateBodyModel'

export const saveNonEventOfferPriceTable = async (
  formValues: PriceTableFormValues,
  {
    offer,
    setError,
  }: {
    offer: GetIndividualOfferWithAddressResponseModel
    setError: UseFormSetError<PriceTableFormValues>
  }
) => {
  const firstEntry = formValues.entries[0]

  try {
    await api.patchOffer(offer.id, { isDuo: formValues.isDuo })

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
  } catch (error) {
    if (isErrorAPIError(error)) {
      const serializedApiErrors = serializeApiErrors(error.body)
      for (const [key, value] of Object.entries(serializedApiErrors)) {
        const message = typeof value === 'string' ? value : value?.join(',  ')
        setError(key as keyof PriceTableFormValues, {
          message,
        })
      }

      if (serializedApiErrors.priceLimitationRule) {
        setError('entries.0.price', { type: 'custom', message: 'Non valide' })
      }
    }

    return handleError(error, FAILED_PATCH_OFFER_USER_MESSAGE)
  }

  await Promise.all([api.getOffer(offer.id), api.getStocks(offer.id)])
}
