import { GetVenueResponseModel } from 'apiClient/v1'
import { IVenue } from 'core/Venue'

export const serializeVenueApi = (venue: GetVenueResponseModel): IVenue => {
  return {
    publicName: venue.publicName || '',
  }
}
