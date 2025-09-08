import type {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

export interface StepPattern {
  id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  label: string | React.ReactNode
  canGoBeyondStep?: (
    offer: GetIndividualOfferWithAddressResponseModel,
    subCategory?: SubcategoryResponseModel
  ) => boolean
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
      canGoBeyondStep: (offer) => Boolean(offer.name),
    },
    {
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS,
      label: isNewOfferCreationFlowFeatureActive
        ? 'Localisation'
        : 'Informations pratiques',
      canGoBeyondStep: (offer) => {
        return Boolean(offer.address)
      },
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
          canGoBeyondStep: (offer) => Boolean(offer?.priceCategories?.length),
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Horaires',
          canGoBeyondStep: (offer) => Boolean(offer?.hasStocks),
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
        label: 'Tarifs',
        canGoBeyondStep: (offer) => Boolean(offer?.hasStocks),
      })
    }
    steps.push({
      id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
      label: 'Informations pratiques',
      canGoBeyondStep: (offer, subCategory) =>
        subCategory?.canBeWithdrawable ? Boolean(offer.bookingContact) : true,
    })
  } else {
    // This part will disappear once the FF is enabled in production.
    if (isEvent) {
      steps.push(
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
          label: 'Tarifs',
          canGoBeyondStep: (offer) => Boolean(offer?.priceCategories?.length),
        },
        {
          id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
          label: 'Dates & Capacités',
          canGoBeyondStep: (offer) => Boolean(offer?.hasStocks),
        }
      )
    } else {
      steps.push({
        id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS,
        label: 'Stock & Prix',
        canGoBeyondStep: (offer) => Boolean(offer?.hasStocks),
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
