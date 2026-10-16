import {
  type GetOffererVenueResponseModel,
  type GetVenueResponseModel,
  type VenueListItemResponseModel,
  VenueState,
} from '@/apiClient/v1'

export function withVenueHelpers(
  venue: GetVenueResponseModel
): GetVenueResponseModel & {
  isClosed: boolean
  fullAddressAsString: string | null
}
export function withVenueHelpers(
  venue: VenueListItemResponseModel
): VenueListItemResponseModel & {
  isClosed: boolean
  fullAddressAsString: string
}
export function withVenueHelpers(
  venue: GetOffererVenueResponseModel
): GetOffererVenueResponseModel & {
  isClosed: boolean
}
export function withVenueHelpers(
  venue:
    | GetVenueResponseModel
    | VenueListItemResponseModel
    | GetOffererVenueResponseModel
) {
  if (!('location' in venue)) {
    return {
      ...venue,
    }
  }

  const isClosed =
    venue.state === VenueState.CLOSED || venue.managingOfferer.isClosed

  return {
    ...venue,

    get fullAddressAsString() {
      if (!venue.location) {
        return null
      }

      const street = venue.location.street ? `${venue.location.street}, ` : ''

      return `${street}${venue.location.postalCode} ${venue.location.city}`
    },

    get isClosed() {
      return isClosed
    },
  }
}
