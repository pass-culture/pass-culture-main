// TODO (rchaffal): once WIP_OFFER_EXPOSURE is enabled for everyone,
//  we can simplify this util by removing all the isOfferExposureEnabled conditions
// and delete the read only mode.

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
  isOfferExposureEnabled?: boolean
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
    [OFFER_WIZARD_MODE.EDITION]: '',
    [OFFER_WIZARD_MODE.READ_ONLY]: '',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.CONFIRMATION]: {
    [OFFER_WIZARD_MODE.CREATION]: `/offre/individuelle/:offerId/creation/confirmation`,
    [OFFER_WIZARD_MODE.EDITION]: '',
    [OFFER_WIZARD_MODE.READ_ONLY]: '',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS]: {
    [OFFER_WIZARD_MODE.CREATION]: '',
    [OFFER_WIZARD_MODE.EDITION]: '/offre/individuelle/:offerId/reservations',
    [OFFER_WIZARD_MODE.READ_ONLY]: '/offre/individuelle/:offerId/reservations',
  },
  [INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE]: {
    [OFFER_WIZARD_MODE.CREATION]: '',
    [OFFER_WIZARD_MODE.EDITION]: '/offre/individuelle/:offerId/visibilite',
    [OFFER_WIZARD_MODE.READ_ONLY]: '/offre/individuelle/:offerId/visibilite',
  },
}

export const getIndividualOfferPath = ({
  isCreation = false,
  mode,
  step,
  isOnboarding = false,
  isOfferExposureEnabled = false,
}: GetIndividualOfferPathArgs): string => {
  if (isCreation) {
    return `${isOnboarding ? '/onboarding' : ''}/offre/individuelle/creation/${step}`
  }

  const modeToUse =
    isOfferExposureEnabled && mode === OFFER_WIZARD_MODE.READ_ONLY
      ? OFFER_WIZARD_MODE.EDITION
      : mode

  return `${isOnboarding ? '/onboarding' : ''}${routes[step][modeToUse]}`
}

interface GetIndividualOfferUrlArgs {
  offerId?: number
  mode: OFFER_WIZARD_MODE
  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  isOnboarding?: boolean
  isOfferExposureEnabled?: boolean
}

export const getIndividualOfferUrl = ({
  offerId,
  mode,
  step,
  isOnboarding = false,
  isOfferExposureEnabled = false,
}: GetIndividualOfferUrlArgs) =>
  generatePath(
    getIndividualOfferPath({
      isCreation: offerId === undefined,
      mode,
      step,
      isOnboarding,
      isOfferExposureEnabled,
    }),
    { offerId: offerId?.toString() }
  )
