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
