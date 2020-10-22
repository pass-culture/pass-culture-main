import { fetchFromApiWithCredentials } from '../utils/fetch'

const EMPTY_PAGINATED_BOOKINGS_RECAP = {
  page: 0,
  pages: 0,
  total: 0,
  bookings_recap: [],
}

export const fetchBookingsRecapByPage = (page = 1) => {
  return fetchFromApiWithCredentials(`/bookings/pro?page=${page}`).catch(
    () => EMPTY_PAGINATED_BOOKINGS_RECAP
  )
}
