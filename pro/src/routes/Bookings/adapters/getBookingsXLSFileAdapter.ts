import { GetBookingsXLSFileAdapter } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur s’est produite. Veuillez réessayer ultérieurement.',
  payload: null,
}

const getBookingsXLSFileAdapter: GetBookingsXLSFileAdapter = async filters => {
  try {
    const bookingsXLSText = await pcapi.getFilteredBookingsXLS({
      bookingPeriodBeginningDate: filters.bookingBeginningDate,
      bookingPeriodEndingDate: filters.bookingEndingDate,
      bookingStatusFilter: filters.bookingStatusFilter,
      eventDate: filters.offerEventDate,
      offerType: filters.offerType,
      venueId: filters.offerVenueId,
      page: filters.page,
    })

    const fakeLink = document.createElement('a')

    const dataToBlob = new Uint8Array(bookingsXLSText)

    const blob = new Blob([dataToBlob], {
      type: 'application/vnd.ms-excel',
    })
    const date = new Date().toISOString()

    fakeLink.href = URL.createObjectURL(blob)
    fakeLink.setAttribute('download', `reservations_pass_culture-${date}.xlsx`)

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

export default getBookingsXLSFileAdapter
