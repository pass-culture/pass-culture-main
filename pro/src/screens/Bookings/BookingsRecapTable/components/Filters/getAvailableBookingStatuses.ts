import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'

import { getBookingStatusDisplayInformations } from '../../utils/bookingStatusConverter'

export function getAvailableBookingStatuses<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(bookingsRecap: T[]) {
  const presentBookingStatues = Array.from(
    new Set(bookingsRecap.map(bookingRecap => bookingRecap.booking_status))
  ).map(bookingStatus => ({
    title: getBookingStatusDisplayInformations(bookingStatus)?.status ?? '',
    value: bookingStatus,
  }))

  const byStatusTitle = (
    bookingStatusA: { title: string },
    bookingStatusB: { title: string }
  ) => {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  return presentBookingStatues.sort(byStatusTitle)
}
