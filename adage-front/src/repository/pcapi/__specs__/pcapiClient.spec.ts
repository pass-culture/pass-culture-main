import fetch from 'jest-fetch-mock'

import { client } from 'repository/pcapi/pcapiClient'
import { API_URL, URL_FOR_MAINTENANCE } from 'utils/config'

Reflect.deleteProperty(global.window, 'location')
const token = 'JWT-token'
window.location.href = `https://www.example.com?token=${token}`
const setHrefSpy = jest.fn()
Object.defineProperty(window.location, 'href', {
  set: setHrefSpy,
})

describe('pcapiClient', () => {
  beforeEach(() => {
    fetch.mockResponse(JSON.stringify({}), { status: 200 })
  })

  afterEach(() => {
    fetch.resetMocks()
  })

  describe('get', () => {
    it('should call API with given path and token in authorization header', async () => {
      // Given
      const path = '/bookings/pro'

      // When
      await client.get(path)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: new Headers({
          Authorization: `Bearer ${token}`,
        }),
        method: 'GET',
      })
    })

    it('should return json if return status is ok and response contains json', async () => {
      // Given
      const oneBooking = {
        beneficiary: {
          email: 'user@example.com',
          firstname: 'First',
          lastname: 'Last',
        },
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
      fetch.mockResponseOnce(JSON.stringify(paginatedBookingRecapReturned), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })

      // When
      const response = await client.get('/bookings/pro')

      // Then
      expect(response.bookings_recap).toHaveLength(1)
      expect(response).toStrictEqual(paginatedBookingRecapReturned)
    })

    it('should reject if return status is not ok', async () => {
      // Given
      fetch.mockResponse('Forbidden', { status: 403 })

      // When
      await expect(client.get('/bookings/pro')).rejects.toStrictEqual({
        errors: 'Forbidden',
        status: 403,
      })
    })

    it('should redirect to maintenance page when status is 503', async () => {
      // Given
      fetch.mockResponse('Service Unavailable', { status: 503 })

      // When
      await expect(client.get('/bookings/pro')).rejects.toStrictEqual({
        errors: 'Service Unavailable',
        status: 503,
      })

      // Then
      expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
    })
  })

  describe('post', () => {
    it('should call API with given path and body and JSON Mime type and correct method', async () => {
      // Given
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      // When
      await client.post(path, body)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: new Headers({
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        }),
        method: 'POST',
        body: '{"key":"value"}',
      })
    })
  })
})
