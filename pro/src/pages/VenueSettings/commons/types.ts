import type { FlatAddressFormValues } from '@/commons/core/shared/types'

export interface VenueSettingsFormValues extends FlatAddressFormValues {
  bookingEmail: string
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  withdrawalDetails: string
  manuallySetAddress?: boolean
}

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  isVenueVirtual: boolean
  siren: string | null
  withSiret: boolean
}
