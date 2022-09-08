import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'
import { IAccessibiltyFormValues } from 'core/shared'

export interface IVenueFormValues {
  accessibility: IAccessibiltyFormValues
  address: string
  addressAutocomplete: string
  additionalAddress: string
  bannerMeta: IVenueBannerMetaProps | undefined | null
  bannerUrl: string | undefined
  city: string
  comment: string
  description: string
  departmentCode: string
  email: string
  id: string
  isAccessibilityAppliedOnAllOffers: boolean
  isPermanent: boolean
  isVenueVirtual: boolean
  latitude: number
  longitude: number
  mail: string
  name: string
  phoneNumber: string
  postalCode: string
  publicName: string
  siret: string
  'search-addressAutocomplete': string
  venueLabel: string
  venueType: string
  webSite: string
}
