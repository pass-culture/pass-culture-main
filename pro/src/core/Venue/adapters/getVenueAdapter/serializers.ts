import { GetVenueResponseModel } from 'apiClient/v1'
import { IVenue } from 'core/Venue'

export const serializeVenueApi = (venue: GetVenueResponseModel): IVenue => {
  return <IVenue>{
    publicName: venue.publicName || '',
    isPermanent: venue.isPermanent,
    bannerMeta: venue.bannerMeta || undefined,
    id: venue.id,
    bannerUrl: venue.bannerUrl,
  }
}
