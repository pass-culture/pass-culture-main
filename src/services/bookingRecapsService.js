import { fetchFromApiWithCredentials } from '../utils/fetch'

export const fetchBookingRecaps = () => {
  return fetchFromApiWithCredentials('/bookings/pro').catch(() => [])
}
