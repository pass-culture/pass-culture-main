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

export interface AddressFormValues {
  'search-addressAutocomplete': string
  addressAutocomplete: string
  banId: string | null
  street: string | null
  postalCode: string
  city: string
  coords: string
  latitude: string
  longitude: string
}
