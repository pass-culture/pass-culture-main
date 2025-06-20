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

//TO DO to be removed or used in the all app 
export interface Address {
  city: string
  latitude: number | null
  longitude: number | null
  postalCode: string
  street: string
  banId: string | null
  manuallySetAddress?: boolean
  inseeCode: string | null
}

export interface AddressFormValues {
  'search-addressAutocomplete': string
  addressAutocomplete: string
  banId: string | null
  street: string | null
  postalCode: string
  inseeCode: string | null
  city: string
  coords: string
  latitude: string
  longitude: string
}
