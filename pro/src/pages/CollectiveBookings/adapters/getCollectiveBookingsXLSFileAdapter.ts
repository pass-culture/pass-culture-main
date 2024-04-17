import { api } from 'apiClient/api'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { GetBookingsXLSFileAdapter } from 'core/Bookings/types'

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur s’est produite. Veuillez réessayer ultérieurement.',
  payload: null,
}

export const getCollectiveBookingsXLSFileAdapter: GetBookingsXLSFileAdapter =
  async (filters) => {
    try {
      const bookingsXLSText = await api.getCollectiveBookingsExcel(
        filters.page,
        filters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
          ? Number(filters.offerVenueId)
          : null,
        filters.offerEventDate,
        // TODO fix PreFiltersParams type to use CollectiveBookingStatusFilter type
        // @ts-expect-error
        filters.bookingStatusFilter as CollectiveBookingStatusFilter,
        filters.bookingBeginningDate,
        filters.bookingEndingDate
      )

      const fakeLink = document.createElement('a')
      const dataToBlob = new Uint8Array(bookingsXLSText)
      const blob = new Blob([dataToBlob], {
        type: 'application/vnd.ms-excel',
      })
      const date = new Date().toISOString()

      fakeLink.href = URL.createObjectURL(blob)
      fakeLink.setAttribute(
        'download',
        `reservations_eac_pass_culture-${date}.xlsx`
      )

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
