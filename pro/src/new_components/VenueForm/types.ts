import { IVenueBannerMetaProps } from 'components/pages/Offerers/Offerer/VenueV1/VenueEdition/ImageVenueUploaderSection/ImageVenueUploaderSection'

export interface IVenueFormValues {
  publicName: string
  isPermanent: boolean
  bannerMeta: IVenueBannerMetaProps | undefined
  id: string
  bannerUrl: string | undefined
  email: string
  phoneNumber: string
  webSite: string
}
