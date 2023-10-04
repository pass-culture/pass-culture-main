import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

export const computeNextStep = (
  mode: OFFER_WIZARD_MODE,
  isEvent: boolean
): OFFER_WIZARD_STEP_IDS => {
  if (mode === OFFER_WIZARD_MODE.EDITION) {
    return OFFER_WIZARD_STEP_IDS.SUMMARY
  } else if (isEvent) {
    return OFFER_WIZARD_STEP_IDS.TARIFS
  }
  return OFFER_WIZARD_STEP_IDS.STOCKS
}
