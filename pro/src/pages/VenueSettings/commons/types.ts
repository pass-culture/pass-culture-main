import type { FlatAddressFormValues } from '@/commons/core/shared/types'

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  isVenueVirtual: boolean
  siren: string | null
  withSiret: boolean
}

export interface VenueSettingsFormValues extends FlatAddressFormValues {
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  withdrawalDetails: string
  manuallySetAddress?: boolean
  bookingEmail?: string
}
