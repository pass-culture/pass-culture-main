import { GetEducationalOffererResponseModel } from '@/apiClient/v1'

const serializeVenues = (
  venues: GetEducationalOffererResponseModel['managedVenues']
): GetEducationalOffererResponseModel['managedVenues'] =>
  venues
    .filter((venue) => !venue.isVirtual)
    .map((venue) => ({
      ...venue,
      name: venue.publicName || venue.name,
    }))

export const serializeEducationalOfferer = (
  offerer: GetEducationalOffererResponseModel
): GetEducationalOffererResponseModel => {
  return {
    ...offerer,
    managedVenues: serializeVenues(offerer.managedVenues),
  }
}
