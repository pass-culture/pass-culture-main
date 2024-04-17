import { api } from 'apiClient/api'
import { OfferType } from 'apiClient/v1'
import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { GetBookingsXLSFileAdapter } from 'core/Bookings/types'

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: 'Une erreur s’est produite. Veuillez réessayer ultérieurement.',
  payload: null,
}

export const getBookingsXLSFileAdapter: GetBookingsXLSFileAdapter = async (
  filters
) => {
  try {
    const bookingsXLSText = await api.getBookingsExcel(
      filters.page,
      filters.offerVenueId !== DEFAULT_PRE_FILTERS.offerVenueId
        ? Number(filters.offerVenueId)
        : null,
      null,
      filters.offerEventDate,
      filters.bookingStatusFilter,
      filters.bookingBeginningDate,
      filters.bookingEndingDate,
      // TODO fix PreFiltersParams type to use OfferType instead of string
      filters.offerType as OfferType
    )

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
