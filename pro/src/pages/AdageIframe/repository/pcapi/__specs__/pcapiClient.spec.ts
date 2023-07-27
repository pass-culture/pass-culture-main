import { vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { API_URL, URL_FOR_MAINTENANCE } from 'utils/config'

import { client } from '../pcapiClient'

const fetchMock = createFetchMock(vi)

Reflect.deleteProperty(global.window, 'location')
const token = 'JWT-token'
const setHrefSpy = vi.fn()

describe('pcapiClient', () => {
  beforeAll(() => {
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        search: `?token=${token}`,
      },
    })

    Object.defineProperty(window.location, 'href', {
      set: setHrefSpy,
    })
  })

  beforeEach(() => {
    fetchMock.mockResponse(JSON.stringify({}), { status: 200 })
  })

  afterEach(() => {
    fetchMock.resetMocks()
  })

  describe('get', () => {
    it('should call API with given path and token in authorization header', async () => {
      const path = '/bookings/pro'

      await client.get(path)

      expect(fetchMock).toHaveBeenCalledWith(`${API_URL}${path}`, {
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
      fetchMock.mockResponseOnce(
        JSON.stringify(paginatedBookingRecapReturned),
        {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }
      )

      // When
      const response = await client.get('/bookings/pro')

      // Then
      expect(response.bookings_recap).toHaveLength(1)
      expect(response).toStrictEqual(paginatedBookingRecapReturned)
    })

    it('should reject if return status is not ok', async () => {
      fetchMock.mockResponse('Forbidden', { status: 403 })

      await expect(client.get('/bookings/pro')).rejects.toStrictEqual({
        errors: 'Forbidden',
        status: 403,
      })
    })

    it('should redirect to maintenance page when status is 503', async () => {
      fetchMock.mockResponse('Service Unavailable', { status: 503 })

      await expect(client.get('/bookings/pro')).rejects.toStrictEqual({
        errors: 'Service Unavailable',
        status: 503,
      })

      expect(setHrefSpy).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
    })
  })

  describe('post', () => {
    it('should call API with given path and body and JSON Mime type and correct method', async () => {
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      await client.post(path, body)

      expect(fetchMock).toHaveBeenCalledWith(`${API_URL}${path}`, {
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
