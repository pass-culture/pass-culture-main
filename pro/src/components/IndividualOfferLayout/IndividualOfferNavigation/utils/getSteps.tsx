import { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

export const RECALCULATED_PROPERTIES = [
  // Recalculated since it depends on the accessibility form current values.
  'accessibility',
  // Recalculated since offer.priceCategories alone is not a sufficient condition, we also need to check if price
  // categories are not empty.
  'priceCategories',
] as const
export type RecalculatedProperty = (typeof RECALCULATED_PROPERTIES)[number]
type SignificativeProperty =
  | keyof GetIndividualOfferResponseModel
  | RecalculatedProperty

export interface StepPattern {
  id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  label: string | React.ReactNode
  // This is to help aknowledge that the step has been submitted.
  // A significative property must be a mandatory field in the form matching the step.
  // If the form has no mandatory property, significativeProperty is null.
  // An optional step is considered submitted when the step previous to it has been submitted.
  significativeProperty: SignificativeProperty | null
}

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
}): StepPattern[] => {
  const steps: StepPattern[] = [
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DETAILS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Description'
        : 'Détails de l’offre',
      significativeProperty: 'name',
    },
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Localisation'
        : 'Informations pratiques',
      significativeProperty: 'accessibility',
    },
  ]

  if (isMediaPageFeatureEnabled) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
      label: 'Image et vidéo',
      significativeProperty: null,
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
          significativeProperty: 'priceCategories',
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Horaires',
          significativeProperty: 'hasStocks',
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        label: 'Tarifs',
        significativeProperty: 'priceCategories',
      })
    }
  } else {
    // This part will disappear once the FF is enabled in production.
    if (isEvent) {
      steps.push(
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          label: 'Tarifs',
          significativeProperty: 'priceCategories',
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Dates & Capacités',
          significativeProperty: 'hasStocks',
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        label: 'Stock & Prix',
        significativeProperty: 'hasStocks',
      })
    }
  }

  if (mode === OFFER_WIZARD_MODE.CREATION) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      label: 'Récapitulatif',
      significativeProperty: null,
    })
  } else if (
    mode === OFFER_WIZARD_MODE.READ_ONLY ||
    mode === OFFER_WIZARD_MODE.EDITION
  ) {
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
      label: <LabelBooking bookingsCount={bookingsCount || 0} />,
      significativeProperty: null,
    })
  }

  return steps
}
