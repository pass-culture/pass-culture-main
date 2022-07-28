import {
  CanOffererCreateCollectiveOffer,
  hasStatusCode,
} from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

const FAILING_RESPONSE: AdapterFailure<{
  isOffererEligibleToEducationalOffer: false
}> = {
  isOk: false,
  message:
    'Une erreur technique est survenue lors de la vérification de votre éligibilité.',
  payload: {
    isOffererEligibleToEducationalOffer: false,
  },
}

const canOffererCreateCollectiveOfferAdapter: CanOffererCreateCollectiveOffer =
  async (structure: string) => {
    try {
      await pcapi.canOffererCreateEducationalOffer(structure)

      return {
        isOk: true,
        message: null,
        payload: {
          isOffererEligibleToEducationalOffer: true,
        },
      }
    } catch (error) {
      if (hasStatusCode(error) && error.status === 404) {
        return {
          isOk: true,
          message: null,
          payload: {
            isOffererEligibleToEducationalOffer: false,
          },
        }
      }

      return FAILING_RESPONSE
    }
  }

export default canOffererCreateCollectiveOfferAdapter
