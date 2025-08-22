import type { UseFormSetError } from 'react-hook-form'

import { api } from '@/apiClient/api'
import {
  getHumanReadableApiError,
  isErrorAPIError,
  serializeApiErrors,
} from '@/apiClient/helpers'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { FrontendError } from '@/commons/errors/FrontendError'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'

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
  } catch {
    throw new FrontendError(
      'Une erreur est survenue lors de la création de votre offre'
    )
  }

  try {
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

      // For this error, we want to display a custom error on the price field
      if (serializedApiErrors.priceLimitationRule) {
        setError('entries.0.price', { type: 'custom', message: 'Non valide' })
      }
    }
    throw new FrontendError(getHumanReadableApiError(error))
  }

  await Promise.all([api.getOffer(offer.id), api.getStocks(offer.id)])
}
