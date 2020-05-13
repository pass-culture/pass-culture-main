import { fetchBookingRecaps } from '../bookingRecapsService'

describe('src | services | bookingRecapsService', () => {
  let mockJsonPromise
  let mockFetchPromise

  beforeEach(() => {
    mockJsonPromise = Promise.resolve([{}])
    mockFetchPromise = Promise.resolve({
      json: () => mockJsonPromise,
    })
    jest.spyOn(global, 'fetch').mockImplementation(() => mockFetchPromise)
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
})
