import { fetchFromApiWithCredentials } from '../fetch'
import { API_URL } from '../config'
import fetch from 'jest-fetch-mock'

describe('fetchFromApiWithCredentials', () => {
  beforeEach(() => {
    fetch.mockResponse(JSON.stringify({}), { status: 200 })
  })

  afterEach(() => {
    fetch.resetMocks()
  })

  it('should call API with given path, credentials, JSON Mime type and GET method by default', async () => {
    // Given
    const path = '/bookings/pro'

    // When
    await fetchFromApiWithCredentials(path)

    // Then
    expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'GET',
    })
  })

  it('should call API with given method', async () => {
    // Given
    const path = '/bookings/pro'
    const method = 'PATCH'

    // When
    await fetchFromApiWithCredentials(path, method)

    // Then
    expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'PATCH',
    })
  })

  it('should add body to API call when provided', async () => {
    // Given
    const path = '/bookings/pro'
    const method = 'PATCH'
    const body = {
      key: 'value',
    }

    // When
    await fetchFromApiWithCredentials(path, method, body)

    // Then
    expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      method: 'PATCH',
      body: '{"key":"value"}',
    })
  })

  it('should return json if return status is ok', async () => {
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
    fetch.mockResponseOnce(JSON.stringify(paginatedBookingRecapReturned), { status: 200 })

    // When
    const response = await fetchFromApiWithCredentials('/bookings/pro')

    // Then
    expect(response.bookings_recap).toHaveLength(1)
    expect(response).toStrictEqual(paginatedBookingRecapReturned)
  })

  it('should reject promise if return status is not ok', async () => {
    // Given
    fetch.mockResponseOnce('Error happened', { status: 401 })

    // When
    const response = fetchFromApiWithCredentials('/bookings/pro')

    // Then
    await expect(response).rejects.toThrow('HTTP error')
  })
})
