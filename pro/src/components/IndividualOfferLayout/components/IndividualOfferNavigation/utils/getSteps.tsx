import type {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

import { LabelBooking } from '../LabelBooking/LabelBooking'

export interface StepPattern {
  id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  label: string | React.ReactNode
  canGoBeyondStep?: (
    offer: GetIndividualOfferWithAddressResponseModel,
    subCategory?: SubcategoryResponseModel
  ) => boolean
}

type GetStepsContext = {
  isEvent: boolean | null
  mode: OFFER_WIZARD_MODE
  bookingsCount?: number | null
}

interface StepDefinition {
  id: StepPattern['id']
  label: StepPattern['label'] | ((ctx: GetStepsContext) => StepPattern['label'])
  shouldInclude?: (ctx: GetStepsContext) => boolean
  buildCanGoBeyondStep?: (
    ctx: GetStepsContext
  ) => StepPattern['canGoBeyondStep'] | undefined
}

const STEP_DEFINITIONS: StepDefinition[] = [
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
    label: 'Description',
    buildCanGoBeyondStep: () => (offer) => Boolean(offer.name),
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCALISATION,
    label: 'Localisation',
    buildCanGoBeyondStep: () => (offer) => Boolean(offer.location ?? offer.url),
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
    label: 'Image et vidéo',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    label: 'Tarifs',
    buildCanGoBeyondStep:
      (ctx) =>
      (offer): boolean => {
        // We also show all possible steps when we don't know yet
        // (meaning `isEvent` is null or undefined).
        if (ctx.isEvent === null || ctx.isEvent === true) {
          return Boolean(offer?.priceCategories?.length)
        }
        return Boolean(offer?.hasStocks)
      },
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
    label: 'Horaires',
    shouldInclude: (ctx) => ctx.isEvent === null || ctx.isEvent === true,
    buildCanGoBeyondStep: () => (offer) => Boolean(offer?.hasStocks),
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
    label: 'Informations pratiques',
    buildCanGoBeyondStep:
      () =>
      (offer, subCategory): boolean =>
        subCategory?.canBeWithdrawable ? Boolean(offer.bookingContact) : true,
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    label: 'Récapitulatif',
    shouldInclude: (ctx) => ctx.mode === OFFER_WIZARD_MODE.CREATION,
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
    label: (ctx) => <LabelBooking bookingsCount={ctx.bookingsCount || 0} />,
    shouldInclude: (ctx) => ctx.mode === OFFER_WIZARD_MODE.READ_ONLY,
  },
]

export const getSteps = ({
  isEvent,
  mode,
  bookingsCount,
}: GetStepsContext): StepPattern[] => {
  const ctx: GetStepsContext = { isEvent, mode, bookingsCount }
  return STEP_DEFINITIONS.filter((def) =>
    def.shouldInclude ? def.shouldInclude(ctx) : true
  ).map<StepPattern>((def) => ({
    id: def.id,
    label: typeof def.label === 'function' ? def.label(ctx) : def.label,
    canGoBeyondStep: def.buildCanGoBeyondStep?.(ctx),
  }))
}
