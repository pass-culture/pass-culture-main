import type { AddressFormValues } from '@/commons/core/shared/types'
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
export interface PhysicalAddressSubformValues extends AddressFormValues {
  isManualEdition: boolean
  isVenueLocation: boolean
  label: string | null
  offerLocation: string
}

// TODO (igabriele, 2025-08-25): Deduce this type from Yup schema (`yup.InferType<typeof LocationValidationSchema>`) to keep a single source of truth.
export interface LocationFormValues {
  location: PhysicalAddressSubformValues | null
  url: string | null
}
