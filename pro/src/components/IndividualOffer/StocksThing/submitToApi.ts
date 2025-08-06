import { UseFormReset, UseFormSetError } from 'react-hook-form'

import { api } from '@/apiClient/api'
import {
  getHumanReadableApiError,
  isErrorAPIError,
  serializeApiErrors,
} from '@/apiClient/helpers'
import { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'

import {
  serializeCreateThingStock,
  serializeUpdateThingStock,
} from './adapters/serializers'
import { StockThingFormValues } from './types'
import { buildInitialValues } from './utils/buildInitialValues'

export const submitToApi = async (
  values: StockThingFormValues,
  offer: GetIndividualOfferWithAddressResponseModel,
  resetForm: UseFormReset<StockThingFormValues>,
  setErrors: UseFormSetError<StockThingFormValues>
) => {
  try {
    await api.patchOffer(offer.id, { isDuo: values.isDuo })
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la création de votre offre'
    )
  }

  try {
    const departementCode = getDepartmentCode(offer)
    if (values.stockId) {
      await api.updateThingStock(
        values.stockId,
        serializeUpdateThingStock(values, departementCode)
      )
    } else {
      await api.createThingStock(
        serializeCreateThingStock(values, offer.id, departementCode)
      )
    }
  } catch (error) {
    if (isErrorAPIError(error)) {
      const serializedApiErrors = serializeApiErrors(error.body)
      for (const [key, value] of Object.entries(serializedApiErrors)) {
        const message = typeof value === 'string' ? value : value?.join(',  ')
        setErrors(key as keyof StockThingFormValues, {
          message,
        })
      }
      // for this error, we want to display a custom error on the price field
      if (serializedApiErrors.priceLimitationRule) {
        setErrors('price', { type: 'custom', message: 'Non valide' })
      }
      if (serializedApiErrors.url) {
        throw new Error(
          'Vous n’avez pas renseigné l’URL d’accès à l’offre dans la page Informations pratiques.'
        )
      }
    }
    throw new Error(getHumanReadableApiError(error))
  }

  const [offerResponse, stockResponse] = await Promise.all([
    api.getOffer(offer.id),
    api.getStocks(offer.id),
  ])
  resetForm(buildInitialValues(offerResponse, stockResponse.stocks))
}
