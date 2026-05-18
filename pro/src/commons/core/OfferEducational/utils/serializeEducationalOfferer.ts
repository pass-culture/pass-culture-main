import type { GetEducationalOffererResponseModel } from '@/apiClient/v1'

const serializeVenues = (
  venues: GetEducationalOffererResponseModel['managedVenues']
): GetEducationalOffererResponseModel['managedVenues'] =>
  venues.map((venue) => ({
    ...venue,
    name: venue.publicName,
  }))

export const serializeEducationalOfferer = (
  offerer: GetEducationalOffererResponseModel
): GetEducationalOffererResponseModel => {
  return {
    ...offerer,
    managedVenues: serializeVenues(offerer.managedVenues),
  }
}
