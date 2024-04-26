export enum Audience {
  INDIVIDUAL = 'individual',
  COLLECTIVE = 'collective',
}

export enum AccessibilityEnum {
  VISUAL = 'visual',
  MENTAL = 'mental',
  AUDIO = 'audio',
  MOTOR = 'motor',
  NONE = 'none',
}

export interface AccessibilityFormValues {
  visual: boolean
  audio: boolean
  motor: boolean
  mental: boolean
  none: boolean
}
