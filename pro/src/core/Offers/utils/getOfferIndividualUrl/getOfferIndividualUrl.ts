import { generatePath } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import { OFFER_WIZARD_MODE } from 'core/Offers'

import {
  getOfferIndividualUrlV2,
  getOfferIndividualPathV2,
} from './getOfferIndividualUrlV2'

interface IGetOfferIndividualPathArgs {
  isCreation?: boolean
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
  isV2?: boolean
}
export const getOfferIndividualPath = ({
  isCreation = false,
  mode,
  step,
  isV2 = false,
}: IGetOfferIndividualPathArgs) => {
  // needed for redirection to old url
  if (isV2) {
    return getOfferIndividualPathV2({
      isCreation,
      mode,
      step,
    })
  }

  if (isCreation) {
    return `/offre/individuelle/creation/informations`
  }

  return {
    [OFFER_WIZARD_STEP_IDS.INFORMATIONS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/informations`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/informations`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/informations`,
    },
    [OFFER_WIZARD_STEP_IDS.STOCKS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/stocks`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/stocks`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/stocks`,
    },
    [OFFER_WIZARD_STEP_IDS.TARIFS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/tarifs`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/tarifs`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/tarifs`,
    },
    [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/recapitulatif`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/recapitulatif`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/recapitulatif`,
    },
    [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/confirmation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/confirmation`,
      [OFFER_WIZARD_MODE.EDITION]: '',
    },
  }[step][mode]
}

interface IGetOfferIndividualUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
  isV2?: boolean
}
const getOfferIndividualUrl = ({
  offerId,
  mode,
  step,
  isV2 = false,
}: IGetOfferIndividualUrlArgs) => {
  if (isV2) {
    return getOfferIndividualUrlV2({
      offerId,
      mode,
      step,
    })
  }

  return generatePath(
    getOfferIndividualPath({
      isCreation: offerId === undefined,
      mode,
      step,
    }),
    { offerId }
  )
}
export default getOfferIndividualUrl
