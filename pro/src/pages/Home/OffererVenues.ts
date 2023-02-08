import { GetOffererVenueResponseModel } from 'apiClient/v1'

export interface OffererVenues {
  physicalVenues: GetOffererVenueResponseModel[]
  virtualVenue: GetOffererVenueResponseModel | null
}

export const INITIAL_OFFERER_VENUES: OffererVenues = {
  physicalVenues: [],
  virtualVenue: null,
}
