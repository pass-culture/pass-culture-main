import { GetEducationalOffererResponseModel } from 'apiClient/v1'

const serializeVenues = (
  venues: GetEducationalOffererResponseModel['managedVenues']
): GetEducationalOffererResponseModel['managedVenues'] =>
  venues
    .filter((venue) => !venue.isVirtual)
    .map((venue) => ({
      ...venue,
      name: venue.publicName || venue.name,
    }))

export const serializeEducationalOfferers = (
  offerers: GetEducationalOffererResponseModel[]
): GetEducationalOffererResponseModel[] =>
  offerers.map((offerer) => ({
    ...offerer,
    managedVenues: serializeVenues(offerer.managedVenues),
  }))
