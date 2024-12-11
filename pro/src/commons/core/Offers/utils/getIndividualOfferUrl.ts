import { generatePath } from 'react-router'

import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'

interface GetIndividualOfferPathArgs {
  isCreation?: boolean
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
  isOnboarding?: boolean
}

const routes = {
  [OFFER_WIZARD_STEP_IDS.DETAILS]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/details`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/details`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/recapitulatif/details`,
  },
  [OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/pratiques`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/pratiques`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/pratiques`,
  },
  [OFFER_WIZARD_STEP_IDS.STOCKS]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/stocks`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/stocks`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/stocks`,
  },
  [OFFER_WIZARD_STEP_IDS.TARIFS]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/tarifs`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/tarifs`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/tarifs`,
  },
  [OFFER_WIZARD_STEP_IDS.SUMMARY]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/recapitulatif`,
    [OFFER_WIZARD_MODE.EDITION]: ``,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/recapitulatif`,
  },
  [OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/confirmation`,
    [OFFER_WIZARD_MODE.EDITION]: '',
    [OFFER_WIZARD_MODE.READ_ONLY]: '',
  },
  [OFFER_WIZARD_STEP_IDS.BOOKINGS]: {
    [OFFER_WIZARD_MODE.CREATION]: ``,
    [OFFER_WIZARD_MODE.EDITION]: '',
    [OFFER_WIZARD_MODE.READ_ONLY]: '/offre/individuelle/:offerId/reservations',
  },
}

export const getIndividualOfferPath = ({
  isCreation = false,
  mode,
  step,
  isOnboarding = false,
}: GetIndividualOfferPathArgs): string => {
  if (isCreation) {
    return `${isOnboarding ? '/onboarding' : ''}/offre/individuelle/creation/details`
  }

  return `${isOnboarding ? '/onboarding' : ''}${routes[step][mode]}`
}

interface GetIndividualOfferUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: OFFER_WIZARD_STEP_IDS
  isOnboarding?: boolean
}

export const getIndividualOfferUrl = ({
  offerId,
  mode,
  step,
  isOnboarding = false,
}: GetIndividualOfferUrlArgs) =>
  generatePath(
    getIndividualOfferPath({
      isCreation: offerId === undefined,
      mode,
      step,
      isOnboarding,
    }),
    { offerId }
  )
