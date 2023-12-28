import {
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
} from 'apiClient/v1'

export const getVirtualVenueFromOfferer = (
  offerer?: GetOffererResponseModel | null
): GetOffererVenueResponseModel | null => {
  if (!offerer?.hasDigitalVenueAtLeastOneOffer) {
    return null
  }

  return offerer?.managedVenues?.find((venue) => venue.isVirtual) ?? null
}

export const getPhysicalVenuesFromOfferer = (
  offerer?: GetOffererResponseModel | null
): GetOffererVenueResponseModel[] =>
  offerer?.managedVenues?.filter((venue) => !venue.isVirtual) ?? []

export const hasOffererAtLeastOnePhysicalVenue = (
  offerer?: GetOffererResponseModel | null
): boolean =>
  offerer?.managedVenues?.some((venue) => !venue.isVirtual && venue.id) ?? false
