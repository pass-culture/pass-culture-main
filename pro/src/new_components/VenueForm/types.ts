import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'

export interface IVenueFormValues {
  address: string
  addressAutocomplete: string
  additionalAddress: string
  bannerMeta: IVenueBannerMetaProps | undefined | null
  bannerUrl: string | undefined
  city: string
  comment: string
  description: string
  email: string
  id: string
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
