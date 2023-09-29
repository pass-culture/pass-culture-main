import { generatePath } from 'react-router-dom'

import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

interface GetIndividualOfferPathArgs {
  isCreation?: boolean
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
}

export const getIndividualOfferPath = ({
  isCreation = false,
  mode,
  step,
}: GetIndividualOfferPathArgs): string => {
  if (isCreation) {
    return `/offre/individuelle/creation/informations`
  }

  return {
    [OFFER_WIZARD_STEP_IDS.INFORMATIONS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/informations`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/informations`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/informations`,
      [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/informations`,
    },
    [OFFER_WIZARD_STEP_IDS.STOCKS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/stocks`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/stocks`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/stocks`,
      [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/stocks`,
    },
    [OFFER_WIZARD_STEP_IDS.TARIFS]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/tarifs`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/tarifs`,
      [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/tarifs`,
      [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/tarifs`,
    },
    [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/recapitulatif`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/recapitulatif`,
      [OFFER_WIZARD_MODE.EDITION]: ``,
      [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/recapitulatif`,
    },
    [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
      [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/confirmation`,
      [OFFER_WIZARD_MODE.DRAFT]: `/offre/individuelle/:offerId/brouillon/confirmation`,
      [OFFER_WIZARD_MODE.EDITION]: '',
      [OFFER_WIZARD_MODE.READ_ONLY]: '',
    },
    [OFFER_WIZARD_STEP_IDS.BOOKINGS]: {
      [OFFER_WIZARD_MODE.CREATION]: ``,
      [OFFER_WIZARD_MODE.DRAFT]: ``,
      [OFFER_WIZARD_MODE.EDITION]: '',
      [OFFER_WIZARD_MODE.READ_ONLY]:
        '/offre/individuelle/:offerId/reservations',
    },
  }[step][mode]
}

interface GetIndividualOfferUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
}

export const getIndividualOfferUrl = ({
  offerId,
  mode,
  step,
}: GetIndividualOfferUrlArgs) =>
  generatePath(
    getIndividualOfferPath({
      isCreation: offerId === undefined,
      mode,
      step,
    }),
    { offerId }
  )
