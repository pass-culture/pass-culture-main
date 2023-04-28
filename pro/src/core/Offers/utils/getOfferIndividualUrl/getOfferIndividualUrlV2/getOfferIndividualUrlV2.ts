import { generatePath } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

interface IGetOfferIndividualPathArgs {
  isCreation?: boolean
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
}

export const getOfferIndividualPathV2 = ({
  isCreation = false,
  mode,
  step,
}: IGetOfferIndividualPathArgs) => {
  if (isCreation) {
    return `/offre/creation/individuel`
  }

  return {
    [OFFER_WIZARD_STEP_IDS.INFORMATIONS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/individuel/creation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/individuel/brouillon`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/individuel/edition`,
    },
    [OFFER_WIZARD_STEP_IDS.STOCKS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/individuel/creation/stocks`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/individuel/brouillon/stocks`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/individuel/stocks`,
    },
    [OFFER_WIZARD_STEP_IDS.TARIFS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/individuel/creation/tarifs`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/individuel/brouillon/tarifs`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/individuel/tarifs`,
    },
    [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/individuel/creation/recapitulatif`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/individuel/brouillon/recapitulatif`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/:offerId/individuel/recapitulatif`,
    },
    [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/:offerId/individuel/creation/confirmation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/:offerId/individuel/brouillon/confirmation`,
      [OFFER_WIZARD_MODE.EDITION]: '',
    },
  }[step][mode]
}

interface IGetOfferIndividualUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
}
const getOfferIndividualUrlV2 = ({
  offerId,
  mode,
  step,
}: IGetOfferIndividualUrlArgs) => {
  return generatePath(
    getOfferIndividualPathV2({
      isCreation: offerId === undefined,
      mode,
      step,
    }),
    { offerId }
  )
}

export default getOfferIndividualUrlV2
