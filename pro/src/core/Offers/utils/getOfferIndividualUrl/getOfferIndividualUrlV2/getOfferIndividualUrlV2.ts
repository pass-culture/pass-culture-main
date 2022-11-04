/* istanbul ignore file: not needed */
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OFFER_WIZARD_MODE } from 'core/Offers'

interface IGetOfferIndividualUrlArgs {
  offerId?: string
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
}

const getOfferIndividualUrlV2 = ({
  offerId,
  mode,
  step,
}: IGetOfferIndividualUrlArgs) => {
  if (!offerId && step === OFFER_WIZARD_STEP_IDS.INFORMATIONS) {
    return `/offre/individuel/creation/informations`
  }

  return {
    [OFFER_WIZARD_STEP_IDS.INFORMATIONS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuelle/creation/informations`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/informations`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/${offerId}/individuel/brouillon`,
    },
    [OFFER_WIZARD_STEP_IDS.STOCKS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuelle/creation/stocks`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/stocks`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/${offerId}/individuel/stocks`,
    },

    [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuelle/creation/recapitulatif`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/recapitulatif`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/${offerId}/individuel/recapitulatif`,
    },
    [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/${offerId}/individuel/creation/confirmation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/${offerId}/individuel/brouillon/confirmation`,
      [OFFER_WIZARD_MODE.EDITION]: '',
    },
  }[step][mode]
}
export default getOfferIndividualUrlV2
