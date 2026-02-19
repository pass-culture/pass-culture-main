export enum Audience {
  INDIVIDUAL = 'individual',
  COLLECTIVE = 'collective',
}

// TODO (igabriele, 2025-07-24): Remove this enum once the FF is enabled in production.
// A DRY functional design should be enough to avoid this (= always manipulate accessibility props via a few dedicated utils).
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
  'search-addressAutocomplete': string | null
  addressAutocomplete: string | null
  banId: string | null
  street: string | null
  postalCode: string
  inseeCode: string | null
  city: string
  coords: string
  latitude: string
  longitude: string
}

export type Currency = 'EUR' | 'XPF'
