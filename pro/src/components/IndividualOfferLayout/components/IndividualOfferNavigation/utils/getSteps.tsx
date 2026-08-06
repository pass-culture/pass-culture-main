import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

import { LabelBooking } from '../LabelBooking/LabelBooking'

export interface StepPattern {
  id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  label: string | React.ReactNode
}

type GetStepsContext = {
  isEvent: boolean | null
  mode: OFFER_WIZARD_MODE
  bookingsCount?: number | null
  isOfferExposureEnabled?: boolean
}

interface StepDefinition {
  id: StepPattern['id']
  label: StepPattern['label'] | ((ctx: GetStepsContext) => StepPattern['label'])
  shouldInclude?: (ctx: GetStepsContext) => boolean
}

const STEP_DEFINITIONS: StepDefinition[] = [
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE,
    label: 'Visibilité',
    shouldInclude: (ctx) =>
      ((ctx.mode === OFFER_WIZARD_MODE.READ_ONLY ||
        ctx.mode === OFFER_WIZARD_MODE.EDITION) &&
        ctx.isOfferExposureEnabled) ??
      false,
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
    label: 'Description',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION,
    label: 'Localisation',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA,
    label: 'Image et vidéo',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS,
    label: 'Tarifs',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE,
    label: 'Horaires et stocks',
    shouldInclude: (ctx) => ctx.isEvent === null || ctx.isEvent === true,
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
    label: 'Informations pratiques',
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
    label: 'Récapitulatif',
    shouldInclude: (ctx) => ctx.mode === OFFER_WIZARD_MODE.CREATION,
  },
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
    label: (ctx) => <LabelBooking bookingsCount={ctx.bookingsCount || 0} />,
    shouldInclude: (ctx) =>
      ctx.mode === OFFER_WIZARD_MODE.READ_ONLY ||
      (ctx.mode === OFFER_WIZARD_MODE.EDITION &&
        ctx.isOfferExposureEnabled === true),
  },
]

export const getSteps = ({
  isEvent,
  mode,
  bookingsCount,
  isOfferExposureEnabled,
}: GetStepsContext): StepPattern[] => {
  const ctx: GetStepsContext = {
    isEvent,
    mode,
    bookingsCount,
    isOfferExposureEnabled,
  }
  return STEP_DEFINITIONS.filter((def) =>
    def.shouldInclude ? def.shouldInclude(ctx) : true
  ).map<StepPattern>((def) => ({
    id: def.id,
    label: typeof def.label === 'function' ? def.label(ctx) : def.label,
  }))
}
