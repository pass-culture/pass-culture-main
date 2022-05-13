import * as pcapi from 'repository/pcapi/pcapi'

import {
  OfferEducationalStockFormValues,
  hasStatusCode,
  hasStatusCodeAndErrorsCode,
} from 'core/OfferEducational'

type Params = {
  offerId: string
  values: Pick<OfferEducationalStockFormValues, 'priceDetail'>
}

type PostEducationalShadowStockAdapter = Adapter<Params, { id: string }, null>

const KNOWN_BAD_REQUEST_CODES: Record<string, string> = {
  EDUCATIONAL_STOCK_ALREADY_EXISTS:
    "Une erreur s'est produite. Les informations date et prix existent déjà pour cette offre.",
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

const postEducationalShadowStockAdapter: PostEducationalShadowStockAdapter =
  async ({ offerId, values }: Params) => {
    const shadowStockPayload = {
      educationalPriceDetail: values.priceDetail,
    }
    try {
      const { collectiveOfferTemplateId } =
        await pcapi.createEducationalShadowStock(offerId, shadowStockPayload)
      return {
        isOk: true,
        message: null,
        payload: {
          id: collectiveOfferTemplateId,
        },
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
      if (hasStatusCode(error) && error.status === 400) {
        return BAD_REQUEST_FAILING_RESPONSE
      } else {
        return UNKNOWN_FAILING_RESPONSE
      }
    }
  }

export default postEducationalShadowStockAdapter
