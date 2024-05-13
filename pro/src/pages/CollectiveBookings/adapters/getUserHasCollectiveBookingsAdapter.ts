import { api } from 'apiClient/api'

export const getUserHasCollectiveBookingsAdapter = async () => {
  const { hasBookings } = await api.getUserHasCollectiveBookings()

  return hasBookings
}
