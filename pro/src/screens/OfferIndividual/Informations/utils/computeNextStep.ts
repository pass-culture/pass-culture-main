import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

export const computeNextStep = (
  mode: OFFER_WIZARD_MODE,
  isSubmittingDraft: boolean,
  isEvent: boolean
): OFFER_WIZARD_STEP_IDS => {
  let nextStep = OFFER_WIZARD_STEP_IDS.STOCKS
  if (mode === OFFER_WIZARD_MODE.EDITION) {
    nextStep = OFFER_WIZARD_STEP_IDS.SUMMARY
  } else if (isEvent && !isSubmittingDraft) {
    nextStep = OFFER_WIZARD_STEP_IDS.TARIFS
  } else if (isSubmittingDraft) {
    nextStep = OFFER_WIZARD_STEP_IDS.INFORMATIONS
  }
  return nextStep
}
