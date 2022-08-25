import { GetVenueResponseModel } from 'apiClient/v1'
import { IVenue } from 'core/Venue'

export const serializeVenueApi = (venue: GetVenueResponseModel): IVenue => {
  return <IVenue>{
    publicName: venue.publicName || '',
    contact: {
      phoneNumber: venue.contact?.phoneNumber || '',
      email: venue.contact?.email || '',
      webSite: venue.contact?.website || '',
    },
    isPermanent: venue.isPermanent,
    bannerMeta: venue.bannerMeta || undefined,
    id: venue.id,
    bannerUrl: venue.bannerUrl,
  }
}
