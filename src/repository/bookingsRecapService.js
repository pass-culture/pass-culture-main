import { ALL_VENUES } from '../components/pages/Bookings/PreFilters/_constants'
import { fetchFromApiWithCredentials } from '../utils/fetch'
import { stringify } from '../utils/query-string'

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
  const queryParams = stringify(params)
  return fetchFromApiWithCredentials(`/bookings/pro?${queryParams}`).catch(
    () => EMPTY_PAGINATED_BOOKINGS_RECAP
  )
}
