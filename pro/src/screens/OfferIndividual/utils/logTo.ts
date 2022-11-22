import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'

export const logTo = (nextLocation: string) => {
  if (nextLocation.includes(OFFER_WIZARD_STEP_IDS.INFORMATIONS)) {
    return OFFER_WIZARD_STEP_IDS.INFORMATIONS
  } else if (nextLocation.includes(OFFER_WIZARD_STEP_IDS.STOCKS)) {
    return OFFER_WIZARD_STEP_IDS.STOCKS
  } else if (nextLocation.includes(OFFER_WIZARD_STEP_IDS.SUMMARY)) {
    return OFFER_WIZARD_STEP_IDS.SUMMARY
  }
  return nextLocation
}
