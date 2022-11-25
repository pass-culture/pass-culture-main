import { generatePath } from 'react-router'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import {
  getOfferIndividualUrlV2,
  getOfferIndividualPathV2,
} from './getOfferIndividualUrlV2'

interface IGetOfferIndividualUrlArgs {
  offerId?: string
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
  isV2?: boolean
}

export const getOfferIndividualPath = ({
  offerId,
  mode,
  step,
  isV2 = false,
}: IGetOfferIndividualUrlArgs) => {
  // remove me when deleting OFFER_FORM_V3
  if (isV2) {
    return getOfferIndividualPathV2({
      offerId,
      mode,
      step,
    })
  }

  if (!offerId && step === OFFER_WIZARD_STEP_IDS.INFORMATIONS) {
    return `/offre/v3/creation/individuelle/informations`
  }
  return {
    [OFFER_WIZARD_STEP_IDS.INFORMATIONS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/v3/creation/individuelle/informations`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/v3/brouillon/individuelle/informations`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/v3/individuelle/informations`,
    },
    [OFFER_WIZARD_STEP_IDS.STOCKS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/v3/creation/individuelle/stocks`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/v3/brouillon/individuelle/stocks`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/v3/individuelle/stocks`,
    },

    [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/v3/creation/individuelle/recapitulatif`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/v3/brouillon/individuelle/recapitulatif`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/v3/individuelle/recapitulatif`,
    },
    [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/v3/creation/individuelle/confirmation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/v3/brouillon/individuelle/confirmation`,
      [OFFER_WIZARD_MODE.EDITION]: '',
    },
  }[step][mode]
}
const getOfferIndividualUrl = ({
  offerId,
  mode,
  step,
  isV2 = false,
}: IGetOfferIndividualUrlArgs) => {
  // remove me when deleting OFFER_FORM_V3
  if (isV2) {
    return getOfferIndividualUrlV2({
      offerId,
      mode,
      step,
    })
  }

  if (!offerId && step === OFFER_WIZARD_STEP_IDS.INFORMATIONS) {
    return `/offre/v3/creation/individuelle/informations`
  }

  return generatePath(
    getOfferIndividualPath({
      offerId,
      mode,
      step,
    }),
    { offerId }
  )
}
export default getOfferIndividualUrl
