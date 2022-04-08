import { GetBookingsCSVFileAdapter } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur s’est produite. Veuillez réessayer ultérieurement.',
  payload: null,
}

export const getBookingsCSVFileAdapter: GetBookingsCSVFileAdapter =
  async filters => {
    try {
      const bookingsCsvText = await pcapi.getFilteredBookingsCSV({
        bookingPeriodBeginningDate: filters.bookingBeginningDate,
        bookingPeriodEndingDate: filters.bookingEndingDate,
        bookingStatusFilter: filters.bookingStatusFilter,
        eventDate: filters.offerEventDate,
        offerType: filters.offerType,
        venueId: filters.offerVenueId,
        page: filters.page,
      })

      const fakeLink = document.createElement('a')
      const blob = new Blob([bookingsCsvText], { type: 'text/csv' })
      const date = new Date().toISOString()

      fakeLink.href = URL.createObjectURL(blob)
      fakeLink.setAttribute('download', `reservations_pass_culture-${date}.csv`)

      document.body.appendChild(fakeLink)

      fakeLink.click()

      document.body.removeChild(fakeLink)

      return {
        isOk: true,
        message: null,
        payload: null,
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getBookingsCSVFileAdapter
