import { fetchBookingRecaps } from '../bookingRecapsService'
import * as fetch from '../../utils/fetch'

describe('src | services | bookingRecapsService', () => {
  let mockJsonPromise

  beforeEach(() => {
    mockJsonPromise = Promise.resolve([])
    jest.spyOn(fetch, 'fetchFromApiWithCredentials').mockImplementation(() => mockJsonPromise)
  })

  it('should return bookingRecaps values', async () => {
    // Given
    const oneBooking = {
      beneficiary: { email: 'user@example.com', firstname: 'First', lastname: 'Last' },
      booking_date: '2020-04-12T19:31:12Z',
      booking_is_duo: false,
      booking_status: 'reimbursed',
      booking_token: 'TOKEN',
      stock: { offer_name: 'My offer name' },
    }
    mockJsonPromise = Promise.resolve([oneBooking])

    // When
    const bookingRecaps = await fetchBookingRecaps()

    // Then
    expect(bookingRecaps).toHaveLength(1)
    expect(bookingRecaps).toStrictEqual([oneBooking])
  })

  it('should return empty list when an error occurred', async () => {
    // Given
    mockJsonPromise = Promise.reject('An error occured')

    // When
    const bookingRecaps = await fetchBookingRecaps()

    // Then
    expect(bookingRecaps).toHaveLength(0)
    expect(bookingRecaps).toStrictEqual([])
  })
})
