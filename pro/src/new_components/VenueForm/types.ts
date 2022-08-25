import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'

export interface IVenueFormValues {
  bannerMeta: IVenueBannerMetaProps | undefined | null
  bannerUrl: string | undefined
  comment: string
  description: string
  email: string
  id: string
  isPermanent: boolean
  isVenueVirtual: boolean
  mail: string
  name: string
  phoneNumber: string
  publicName: string
  siret: string
  venueLabel: string
  venueType: string
  webSite: string
}
