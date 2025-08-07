import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferPath } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { StepPattern } from '@/components/Stepper/Stepper'

import { LabelBooking } from '../LabelBooking/LabelBooking'

export const getSteps = ({
  isMediaPageFeatureEnabled,
  isNewOfferCreationFlowFeatureActive,
  isEvent,
  mode,
  bookingsCount,
}: {
  isMediaPageFeatureEnabled: boolean
  isNewOfferCreationFlowFeatureActive: boolean
  isEvent: boolean | null
  mode: OFFER_WIZARD_MODE
  bookingsCount?: number | null
}) => {
  const steps: StepPattern[] = [
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Description'
        : 'Détails de l’offre',
    },
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Localisation'
        : 'Informations pratiques',
    },
  ]

  if (isMediaPageFeatureEnabled) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      label: 'Image et vidéo',
    })
  }

  // We also show all possible steps when we don't know yet
  // (meaning `isEvent` is null or undefined).
  if (isNewOfferCreationFlowFeatureActive) {
    if (isEvent === null || isEvent) {
      steps.push(
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          label: 'Tarifs',
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Horaires',
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        label: 'Tarifs',
      })
    }
  } else {
    // This part will disappear once the FF is enabled in production.
    if (isEvent) {
      steps.push(
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          label: 'Tarifs',
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Dates & Capacités',
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        label: 'Stock & Prix',
      })
    }
  }

  if (mode === OFFER_WIZARD_MODE.CREATION) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
    })
  } else if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
      label: <LabelBooking bookingsCount={bookingsCount || 0} />,
    })
  }

  return steps
}
