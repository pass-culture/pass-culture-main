import { ALL_VENUES } from 'components/pages/Bookings/PreFilters/_constants'

import { loadFilteredBookingsRecap } from './pcapi/pcapi'

const EMPTY_PAGINATED_BOOKINGS_RECAP = {
  page: 0,
  pages: 0,
  total: 0,
  bookings_recap: [],
}

export const fetchBookingsRecapByPage = (page, filters) => {
  const params = {
    page,
  }
  if (filters && filters?.venueId !== ALL_VENUES) {
    params.venueId = filters.venueId
  }
  return loadFilteredBookingsRecap(params).catch(() => EMPTY_PAGINATED_BOOKINGS_RECAP)
}
