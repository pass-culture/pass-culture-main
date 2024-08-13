import { api } from 'apiClient/api'
import {
  getHumanReadableApiError,
  isErrorAPIError,
  serializeApiErrors,
} from 'apiClient/helpers'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'

import { serializeStockThingList } from './adapters/serializers'
import { StockThingFormValues, StockThingFormik } from './types'
import { buildInitialValues } from './utils/buildInitialValues'

export const submitToApi = async (
  values: StockThingFormValues,
  offer: GetIndividualOfferResponseModel,
  resetForm: StockThingFormik['resetForm'],
  setErrors: StockThingFormik['setErrors']
) => {
  try {
    await api.patchOffer(offer.id, { isDuo: values.isDuo })
  } catch {
    throw new Error(
      'Une erreur est survenue lors de la création de votre offre'
    )
  }

  try {
    await api.upsertStocks({
      offerId: offer.id,
      stocks: serializeStockThingList(values, offer.venue.departementCode),
    })
  } catch (error) {
    if (isErrorAPIError(error)) {
      const serializedApiErrors = serializeApiErrors(error.body)
      setErrors(serializedApiErrors)
      // for this error, we want to display a custom error on the price field
      if (serializedApiErrors.priceLimitationRule) {
        setErrors({ price: 'Non valide' })
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
  resetForm({
    values: buildInitialValues(offerResponse, stockResponse.stocks),
  })
}
