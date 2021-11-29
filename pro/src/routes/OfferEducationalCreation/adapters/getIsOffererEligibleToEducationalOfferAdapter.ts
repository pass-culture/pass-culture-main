import { GetIsOffererEligibleToEducationalOffer } from 'core/OfferEducational'
import * as pcapi from 'repository/pcapi/pcapi'

import { hasStatusCode } from './utils'

const FAILING_RESPONSE = {
  isOk: false,
  message:
    "Une erreur est survenue lors de la vérification de votre éligibilité à la création d'offre collective",
  payload: {
    isOffererEligibleToEducationalOffer: false,
  },
}

const getIsOffererEligibleToEducationalOfferAdapter: GetIsOffererEligibleToEducationalOffer =
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
      if (hasStatusCode(error) && error.status === 403) {
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

export default getIsOffererEligibleToEducationalOfferAdapter
