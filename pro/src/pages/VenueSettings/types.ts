import { AddressFormValues } from 'components/AddressManual/AddressManual'

export interface VenueSettingsFormValues extends AddressFormValues {
  bookingEmail: string
  comment: string
  isWithdrawalAppliedOnAllOffers: boolean
  name: string
  publicName: string
  siret: string
  venueSiret: number | null
  venueLabel: string | null
  venueType: string
  withdrawalDetails: string
  manuallySetAddress?: boolean
}
