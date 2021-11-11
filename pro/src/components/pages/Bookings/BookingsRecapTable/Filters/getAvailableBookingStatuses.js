import { getBookingStatusDisplayInformations } from '../CellsFormatter/utils/bookingStatusConverter'

export function getAvailableBookingStatuses(bookingsRecap) {
  const presentBookingStatues = Array.from(
    new Set(bookingsRecap.map(bookingRecap => bookingRecap.booking_status))
  ).map(bookingStatus => ({
    title: getBookingStatusDisplayInformations(bookingStatus).status,
    value: bookingStatus,
  }))

  const byStatusTitle = (bookingStatusA, bookingStatusB) => {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  return presentBookingStatues.sort(byStatusTitle)
}
