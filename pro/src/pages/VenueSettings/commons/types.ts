import type { AddressFormValues } from '@/commons/core/shared/types'

export interface VenueSettingsFormValues extends AddressFormValues {
  bookingEmail: string
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  venueType: string
  withdrawalDetails: string
  manuallySetAddress?: boolean
}

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  isVenueVirtual: boolean
  siren: string | null
  withSiret: boolean
}

export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
