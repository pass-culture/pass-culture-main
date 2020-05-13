import { API_URL } from '../utils/config'

export const fetchBookingRecaps = () => {
  return fetch(`${API_URL}/bookings/pro`, { credentials: 'include' })
    .then(response => response.json())
    .catch(() => [])
}
