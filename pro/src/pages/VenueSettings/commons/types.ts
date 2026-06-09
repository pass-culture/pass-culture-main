import type { ActivityNotOpenToPublicType } from '@/commons/mappings/ActivityNotOpenToPublic'
import type { ActivityOpenToPublicType } from '@/commons/mappings/ActivityOpenToPublic'

export type VenueSettingsFormContext = {
  isCaledonian: boolean
  siren: string | null
  withSiret: boolean
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
}

export interface VenueSettingsFormValues {
  comment: string
  name: string
  publicName: string
  siret: string
  venueSiret: number | ''
  withdrawalDetails: string
  manuallySetAddress?: boolean
  bookingEmail?: string
  isOpenToPublic: string
  activity?: ActivityOpenToPublicType | ActivityNotOpenToPublicType | null
  culturalDomains?: string[]
  description?: string
  'search-addressAutocomplete': string | null
  addressAutocomplete: string | null
  banId: string | null
  street: string | null
  postalCode: string | null
  inseeCode: string | null
  city: string | null
  coords: string | null
  latitude: string | null
  longitude: string | null
}
