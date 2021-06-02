import { ALL_VENUES } from '../../components/pages/Bookings/PreFilters/_constants'
import * as fetch from '../../utils/fetch'
import { fetchBookingsRecapByPage } from '../bookingsRecapService'

describe('bookingRecapsService', () => {
  let mockJsonPromise
  let fetchFromApiWithCredentialsStub

  beforeEach(() => {
    mockJsonPromise = Promise.resolve({
      page: 0,
      pages: 0,
      total: 0,
      bookings_recap: [],
    })
    fetchFromApiWithCredentialsStub = jest
      .spyOn(fetch, 'fetchFromApiWithCredentials')
      .mockImplementation(() => mockJsonPromise)
  })

  it('should call API with given page', async () => {
    // Given
    const page = 3

    // When
    await fetchBookingsRecapByPage(page)

    // Then
    expect(fetchFromApiWithCredentialsStub).toHaveBeenCalledWith(`/bookings/pro?page=${page}`)
  })

  it('should return paginatedBookingsRecap value', async () => {
    // Given
    const oneBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    const paginatedBookingRecapReturned = {
      page: 1,
      pages: 1,
      total: 1,
      bookings_recap: [oneBooking],
    }
    mockJsonPromise = Promise.resolve(paginatedBookingRecapReturned)

    // When
    const paginatedBookingsRecap = await fetchBookingsRecapByPage()

    // Then
    expect(paginatedBookingsRecap.bookings_recap).toHaveLength(1)
    expect(paginatedBookingsRecap).toStrictEqual(paginatedBookingRecapReturned)
  })

  it('should return empty paginatedBookingsRecap when an error occurred', async () => {
    // Given
    mockJsonPromise = Promise.reject('An error occured')
    const emptyPaginatedBookingsRecap = {
      page: 0,
      pages: 0,
      total: 0,
      bookings_recap: [],
    }

    // When
    const bookingRecaps = await fetchBookingsRecapByPage(1, {})

    // Then
    expect(bookingRecaps.bookings_recap).toHaveLength(0)
    expect(bookingRecaps).toStrictEqual(emptyPaginatedBookingsRecap)
  })

  it('should call API with given venueId', () => {
    // Given
    const venueId = 'A3HC'

    // When
    fetchBookingsRecapByPage(1, { venueId: venueId })

    // Then
    expect(fetchFromApiWithCredentialsStub).toHaveBeenCalledWith(
      `/bookings/pro?page=1&venueId=${venueId}`
    )
  })

  it('should call API with no venueId param when requesting all venues', () => {
    // Given
    const venueId = ALL_VENUES

    // When
    fetchBookingsRecapByPage(1, { venueId: venueId })

    // Then
    expect(fetchFromApiWithCredentialsStub).toHaveBeenCalledWith(`/bookings/pro?page=1`)
  })
})
