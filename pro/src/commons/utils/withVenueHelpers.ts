import {
  type GetOffererVenueResponseModel,
  type GetVenueResponseModel,
  type VenueListItemLiteResponseModel,
  VenueState,
} from '@/apiClient/v1'

export function withVenueHelpers(
  venue: GetVenueResponseModel
): GetVenueResponseModel & {
  isClosedOrClosing: boolean
  fullAddressAsString: string | null
}
export function withVenueHelpers(
  venue: VenueListItemLiteResponseModel
): VenueListItemLiteResponseModel & {
  isClosedOrClosing: boolean
  fullAddressAsString: string
}
export function withVenueHelpers(
  venue: GetOffererVenueResponseModel
): GetOffererVenueResponseModel & {
  isClosedOrClosing: boolean
}
export function withVenueHelpers(
  venue:
    | GetVenueResponseModel
    | VenueListItemLiteResponseModel
    | GetOffererVenueResponseModel
) {
  if (!('location' in venue)) {
    return {
      ...venue,
    }
  }

  const isClosedOrClosing =
    venue.state === VenueState.CLOSED ||
    venue.state === VenueState.CLOSING ||
    venue.managingOfferer.isClosed

  return {
    ...venue,

    get fullAddressAsString() {
      if (!venue.location) {
        return null
      }

      const street = venue.location.street ? `${venue.location.street}, ` : ''

      return `${street}${venue.location.postalCode} ${venue.location.city}`
    },

    get isClosedOrClosing() {
      return isClosedOrClosing
    },
  }
}
