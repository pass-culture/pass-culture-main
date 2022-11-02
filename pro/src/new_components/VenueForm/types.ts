import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import { IAccessibiltyFormValues } from 'core/shared'

export interface IVenueFormValues {
  reimbursementPointId: number | null
  accessibility: IAccessibiltyFormValues
  address: string
  addressAutocomplete: string
  bannerMeta: IVenueBannerMetaProps | undefined | null
  bannerUrl: string | undefined
  city: string
  comment: string
  description: string
  departmentCode: string
  email: string | null
  id: string
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
