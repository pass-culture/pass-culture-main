import {
  type INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'

export const getAfterSubmitPath = ({
  currentStep,
  followingStep,
  isOfferExposureEnabled,
  isOnboarding,
  mode,
  offerId,
}: {
  currentStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  followingStep: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  isOfferExposureEnabled: boolean
  isOnboarding: boolean
  mode: OFFER_WIZARD_MODE
  offerId?: number
}): string | undefined => {
  if (isOfferExposureEnabled && mode !== OFFER_WIZARD_MODE.CREATION) {
    return undefined
  }

  let nextMode: OFFER_WIZARD_MODE
  if (isOfferExposureEnabled) {
    nextMode = mode
  } else {
    nextMode =
      mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode
  }

  return getIndividualOfferUrl({
    isOnboarding,
    mode: nextMode,
    offerId,
    step: mode === OFFER_WIZARD_MODE.CREATION ? followingStep : currentStep,
  })
}
