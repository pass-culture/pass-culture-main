import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'

export interface StepPattern {
  id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS
  label: string | React.ReactNode
}

type GetStepsContext = {
  isEvent: boolean | null
  mode: OFFER_WIZARD_MODE
}

interface StepDefinition {
  id: StepPattern['id']
  label: StepPattern['label']
  shouldInclude?: (ctx: GetStepsContext) => boolean
}

const isOfferAlreadyCreated = (ctx: GetStepsContext) =>
  ctx.mode === OFFER_WIZARD_MODE.EDITION

const STEP_DEFINITIONS: StepDefinition[] = [
  {
    id: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE,
    label: 'Visibilité',
    shouldInclude: isOfferAlreadyCreated,
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
    label: 'Réservations',
    shouldInclude: isOfferAlreadyCreated,
  },
]

export const getSteps = ({ isEvent, mode }: GetStepsContext): StepPattern[] => {
  const ctx: GetStepsContext = {
    isEvent,
    mode,
  }
  return STEP_DEFINITIONS.filter((def) =>
    def.shouldInclude ? def.shouldInclude(ctx) : true
  ).map<StepPattern>((def) => ({
    id: def.id,
    label: def.label,
  }))
}
