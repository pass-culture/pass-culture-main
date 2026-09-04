import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'

import { withVenueHelpers } from './withVenueHelpers'

export function isSelectedPartnerOrOffererClosed(
  venue: GetVenueResponseModel,
  offerer?: GetOffererResponseModel
) {
  const isOffererClosed = offerer
    ? offerer.isClosed
    : venue.managingOfferer.isClosed
  return withVenueHelpers(venue).isClosed || isOffererClosed
}
