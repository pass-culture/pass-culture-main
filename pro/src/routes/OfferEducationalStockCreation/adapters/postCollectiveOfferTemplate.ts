import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import {
  OfferEducationalStockFormValues,
  hasStatusCodeAndErrorsCode,
} from 'core/OfferEducational'

type Params = {
  offerId: string
  values: Pick<OfferEducationalStockFormValues, 'priceDetail'>
}

type PostCollectiveOfferTemplateAdapter = Adapter<Params, { id: string }, null>

const KNOWN_BAD_REQUEST_CODES: Record<string, string> = {
  EDUCATIONAL_STOCK_ALREADY_EXISTS:
    "Une erreur s'est produite. Les informations date et prix existent déjà pour cette offre.",
  COLLECTIVE_OFFER_NOT_FOUND:
    "Une erreur s'est produite. L'offre n'a pas été trouvée.",
}

const BAD_REQUEST_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une ou plusieurs erreurs sont présentes dans le formulaire',
  payload: null,
}

const UNKNOWN_FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur est survenue lors de la création de votre stock.',
  payload: null,
}

const postCollectiveOfferTemplateAdapter: PostCollectiveOfferTemplateAdapter =
  async ({ offerId, values }: Params) => {
    const collectiveOfferTemplatePayload = {
      educationalPriceDetail: values.priceDetail,
    }
    try {
      const { id } = await api.createCollectiveOfferTemplateFromCollectiveOffer(
        offerId,
        collectiveOfferTemplatePayload
      )
      return {
        isOk: true,
        message: null,
        payload: { id },
      }
    } catch (error) {
      if (hasStatusCodeAndErrorsCode(error) && error.status === 400) {
        if (error.errors.code in KNOWN_BAD_REQUEST_CODES) {
          return {
            ...BAD_REQUEST_FAILING_RESPONSE,
            message: KNOWN_BAD_REQUEST_CODES[error.errors.code],
          }
        }
      }
      if (isErrorAPIError(error) && error.status === 400) {
        return BAD_REQUEST_FAILING_RESPONSE
      } else {
        return UNKNOWN_FAILING_RESPONSE
      }
    }
  }

export default postCollectiveOfferTemplateAdapter
