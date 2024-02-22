import { GetVenueResponseModel } from 'apiClient/v1'
import { Venue } from 'core/Venue/types'

export const serializeVenueApi = (venue: GetVenueResponseModel): Venue => {
  /* istanbul ignore next: DEBT, TO FIX */
  return {
    ...venue,
  }
}
