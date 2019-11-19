import { sortByDateAntechronologically } from '../utils/date/sortByDateAntechronologically'

export const markAsCancelled = bookings => items =>
  items.map(item => {
    const sortedMatchingBookings = bookings
      .sort(sortByDateAntechronologically)
      .find(booking => booking.stockId === item.id)
    const userHasCancelledThisDate =
      (sortedMatchingBookings && sortedMatchingBookings.isCancelled) || false
    return { ...item, userHasCancelledThisDate }
  })
