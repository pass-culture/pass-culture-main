import {
  type INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'

export const getAfterSubmitPath = ({
  followingStep,
  isOnboarding,
  mode,
  offerId,
}: {
  followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  isOnboarding: boolean
  mode: OFFER_WIZARD_MODE
  offerId?: number
}): string | undefined => {
  if (mode !== OFFER_WIZARD_MODE.CREATION) {
    return undefined
  }

  return getIndividualOfferUrl({
    isOnboarding,
    mode,
    offerId,
    step: followingStep,
  })
}
