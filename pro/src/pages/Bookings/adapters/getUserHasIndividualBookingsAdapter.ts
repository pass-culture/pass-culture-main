import { api } from '@/apiClient//api'

export const getUserHasIndividualBookingsAdapter = async () => {
  const { hasBookings } = await api.getUserHasBookings()

  return hasBookings
}
