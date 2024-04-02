import { BannerMetaModel } from 'apiClient/v1'
import { AccessibiltyFormValues } from 'core/shared'

export interface VenueCreationFormValues {
  accessibility: AccessibiltyFormValues
  addressAutocomplete: string
  bannerMeta?: BannerMetaModel | null
  bannerUrl: string | undefined
  banId: string
  bookingEmail: string
  city: string
  comment: string
  latitude: number
  longitude: number
  name: string
  postalCode: string
  publicName: string
  siret: string
  'search-addressAutocomplete': string
  street: string
  venueType: string
}
