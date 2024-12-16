import { type EnumType } from 'commons/custom_types/utils'

export const Audience = {
  INDIVIDUAL: 'individual',
  COLLECTIVE: 'collective',
} as const
// eslint-disable-next-line no-redeclare
export type Audience = EnumType<typeof Audience>

export const AccessibilityEnum = {
  VISUAL: 'visual',
  MENTAL: 'mental',
  AUDIO: 'audio',
  MOTOR: 'motor',
  NONE: 'none',
} as const
// eslint-disable-next-line no-redeclare
export type AccessibilityEnum = EnumType<typeof AccessibilityEnum>

export interface AccessibilityFormValues {
  visual: boolean
  audio: boolean
  motor: boolean
  mental: boolean
  none: boolean
}
