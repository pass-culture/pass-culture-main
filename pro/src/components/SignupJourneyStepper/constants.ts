import { type EnumType } from 'commons/custom_types/utils'

export const SIGNUP_JOURNEY_STEP_IDS = {
  WELCOME: 'inscription',
  OFFERER: 'structure',
  OFFERERS: 'structures',
  OFFERERS_CONFIRMED_ATTACHMENT: 'confirmation',
  AUTHENTICATION: 'identification',
  ACTIVITY: 'activite',
  VALIDATION: 'validation',
  COMPLETED: 'completed',
} as const
// eslint-disable-next-line no-redeclare, @typescript-eslint/naming-convention
export type SIGNUP_JOURNEY_STEP_IDS = EnumType<typeof SIGNUP_JOURNEY_STEP_IDS>
