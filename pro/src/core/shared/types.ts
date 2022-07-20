export enum Audience {
  INDIVIDUAL = 'individual',
  COLLECTIVE = 'collective',
}

export enum AccessiblityEnum {
  VISUAL = 'visual',
  MENTAL = 'mental',
  AUDIO = 'audio',
  MOTOR = 'motor',
  NONE = 'none',
}

export interface IAccessibiltyFormValues {
  visual: boolean
  audio: boolean
  motor: boolean
  mental: boolean
  none: boolean
}
