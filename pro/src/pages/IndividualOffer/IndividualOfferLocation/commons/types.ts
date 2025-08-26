import type { AnyObject } from '@/commons/utils/types'

/**
 * Transform all non-boolean properties of T into `T | null`, while keeping boolean properties as `boolean`.
 *
 * @description
 * This is useful for initializing form values from scratch when we don't have existing data to populate them.
 */
export type NullableIfNonBoolean<T extends AnyObject> = {
  [K in keyof T]: T[K] extends boolean ? T[K] : T[K] | null
}

// TODO (igabriele, 2025-08-25): We can get rid of `isManualEdition` and `offerLocation` to only use `isVenueAddress` + `banId` (Frontend + Backend).
export interface PhysicalAddressSubformValues {
  addressAutocomplete: string | null
  banId: string | null
  city: string
  coords: string | null
  inseeCode: string | null
  isManualEdition: boolean
  isVenueAddress: boolean
  label: string | null
  latitude: string
  longitude: string
  offerLocation: string
  postalCode: string
  'search-addressAutocomplete': string | null
  street: string
}

// TODO (igabriele, 2025-08-25): Deduce this type from Yup schema (`yup.InferType<typeof LocationValidationSchema>`) to keep a single source of truth.
export interface LocationFormValues {
  address: PhysicalAddressSubformValues | null
  url: string | null
}
