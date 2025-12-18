import { generatePath } from 'react-router'

import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

interface GetIndividualOfferPathArgs {
  isCreation?: boolean
  mode: OFFER_WIZARD_MODE
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  isOnboarding?: boolean
}

const routes = {
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/description`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/description`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/recapitulatif/description`,
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/localisation`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/localisation`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/localisation`,
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/media`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/media`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/media`,
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/horaires`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/horaires`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/horaires`,
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/tarifs`,
    [OFFER_WIZARD_MODE.EDITION]: `/offre/individuelle/:offerId/edition/tarifs`,
    [OFFER_WIZARD_MODE.READ_ONLY]: `/offre/individuelle/:offerId/tarifs`,
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS]: {
    [OFFER_WIZARD_MODE.CREATION]:
      '/offre/individuelle/:offerId/creation/informations_pratiques',
    [OFFER_WIZARD_MODE.EDITION]:
      '/offre/individuelle/:offerId/edition/informations_pratiques',
    [OFFER_WIZARD_MODE.READ_ONLY]:
      '/offre/individuelle/:offerId/informations_pratiques',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/recapitulatif`,
    [OFFER_WIZARD_MODE.EDITION]: ``,
    [OFFER_WIZARD_MODE.READ_ONLY]: '',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/confirmation`,
    [OFFER_WIZARD_MODE.EDITION]: '',
    [OFFER_WIZARD_MODE.READ_ONLY]: '',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS]: {
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
    return `${isOnboarding ? '/onboarding' : ''}/offre/individuelle/creation/${step}`
  }

  return `${isOnboarding ? '/onboarding' : ''}${routes[step][mode]}`
}

interface GetIndividualOfferUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
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
