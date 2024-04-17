import { api } from 'apiClient/api'
import { CollectiveBookingStatusFilter } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { GetBookingsCSVFileAdapter } from 'core/Bookings/types'

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur s’est produite. Veuillez réessayer ultérieurement.',
  payload: null,
}

export const getCollectiveBookingsCSVFileAdapter: GetBookingsCSVFileAdapter =
  async (filters) => {
    try {
      const bookingsCsvText = await api.getCollectiveBookingsCsv(
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
      const blob = new Blob([bookingsCsvText], { type: 'text/csv' })
      const date = new Date().toISOString()

      fakeLink.href = URL.createObjectURL(blob)
      fakeLink.setAttribute(
        'download',
        `reservations_eac_pass_culture-${date}.csv`
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
