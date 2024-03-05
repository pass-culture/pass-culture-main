import { BannerMetaModel } from 'apiClient/v1'
import { AccessibiltyFormValues } from 'core/shared'

export interface VenueEditionFormValues {
  reimbursementPointId: number | string | null
  accessibility: AccessibiltyFormValues
  address: string
  addressAutocomplete: string
  banId: string
  bannerMeta?: BannerMetaModel | null
  bannerUrl: string | undefined
  city: string
  comment: string
  description: string
  departmentCode: string
  email: string | null
  id: number | undefined
  isAccessibilityAppliedOnAllOffers: boolean
  isPermanent: boolean
  isVenueVirtual: boolean
  latitude: number
  longitude: number
  bookingEmail: string
  name: string
  phoneNumber: string | null
  venueSiret: number | null
  postalCode: string
  publicName: string
  siret: string
  'search-addressAutocomplete': string
  venueLabel: string | null
  venueType: string
  webSite: string | null
  withdrawalDetails: string
  isWithdrawalAppliedOnAllOffers: boolean
}
