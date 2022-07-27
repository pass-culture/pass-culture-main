import fetch from 'jest-fetch-mock'

import { client } from 'repository/pcapi/pcapiClient'
import { API_URL, URL_FOR_MAINTENANCE } from 'utils/config'

describe('pcapiClient', () => {
  beforeEach(() => {
    fetch.mockResponse(JSON.stringify({}), { status: 200 })
  })

  afterEach(() => {
    fetch.resetMocks()
  })

  describe('getPlainText', () => {
    it('should call API with given path and JSON Mime type and credentials by default and correct method', async () => {
      // Given
      const path = '/bookings/csv'

      // When
      await client.getPlainText(path)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        method: 'GET',
        headers: { 'Content-Type': 'text/plain' },
      })
    })

    it('should return text if response status is 200', async () => {
      // Given
      const responseText = "i'm a response text"
      fetch.mockResponseOnce(responseText, { status: 200 })

      // When
      const response = await client.getPlainText('/bookings/csv')

      // Then
      expect(response).toStrictEqual(responseText)
    })

    it('should reject if return response status is not 200', async () => {
      // Given
      fetch.mockResponseOnce('API error message', { status: 403 })

      // When
      await expect(client.getPlainText('/bookings/csv')).rejects.toStrictEqual(
        new Error('An error happened.')
      )
    })

    it('should throw an error if return response status is not 200', async () => {
      fetch.mockResponseOnce('API error message', { status: 403 })
      let throwError
      try {
        await client.getPlainText('/bookings/csv')
      } catch (e) {
        throwError = e
      }

      expect(throwError).toStrictEqual(new Error('An error happened.'))
    })
  })

  describe('get', () => {
    it('should call API with given path and JSON Mime type and credentials by default and correct method', async () => {
      // Given
      const path = '/bookings/pro'

      // When
      await client.get(path)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        method: 'GET',
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/bookings/pro'

      // When
      await client.get(path, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        method: 'GET',
      })
    })

    it('should return json if return status is ok', async () => {
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
      })

      // When
      const response = await client.get('/bookings/pro')

      // Then
      expect(response.bookings_recap).toHaveLength(1)
      expect(response).toStrictEqual(paginatedBookingRecapReturned)
    })

    it('should reject if return status is not ok', async () => {
      // Given
      fetch.mockResponse(JSON.stringify('Forbidden'), { status: 403 })

      // When
      await expect(client.get('/bookings/pro')).rejects.toStrictEqual({
        errors: 'Forbidden',
        status: 403,
      })
    })

    it('should redirect to maintenance page when status is 503', async () => {
      fetch.mockResponse('Service Unavailable', { status: 503 })
      const mockLocationAssign = jest.fn()
      Object.defineProperty(window, 'location', {
        value: {
          assign: mockLocationAssign,
        },
        configurable: true,
        enumerable: true,
        writable: true,
      })

      await expect(client.get('/bookings/pro')).rejects.toBeNull()

      expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
    })
  })

  describe('post', () => {
    it('should call API with given path and body and JSON Mime type and credentials by default and correct method', async () => {
      // Given
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      // When
      await client.post(path, body)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
        body: '{"key":"value"}',
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      // When
      await client.post(path, body, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
        body: '{"key":"value"}',
      })
    })
  })

  describe('postWithFormData', () => {
    it('should call API with given path and formData and credentials by default and correct method', async () => {
      // Given
      const path = '/mediations'
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('offererId', 'BB')
      body.append('credit', 'Mon crédit')
      body.append('croppingRect[x]', '12')
      body.append('croppingRect[y]', '32')
      body.append('croppingRect[height]', '350')
      body.append('thumb', file)

      // When
      await client.postWithFormData(path, body)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        headers: { encode: 'multipart/form-data' },
        method: 'POST',
        body: body,
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/mediations'
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('offererId', 'BB')
      body.append('credit', 'Mon crédit')
      body.append('croppingRect[x]', '12')
      body.append('croppingRect[y]', '32')
      body.append('croppingRect[height]', '350')
      body.append('thumb', file)

      // When
      await client.postWithFormData(path, body, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: { encode: 'multipart/form-data' },
        method: 'POST',
        body: body,
      })
    })
  })

  describe('patch', () => {
    it('should call API with given path and body and JSON Mime type and credentials by default and correct method', async () => {
      // Given
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      // When
      await client.patch(path, body)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        method: 'PATCH',
        body: '{"key":"value"}',
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/bookings/pro'
      const body = {
        key: 'value',
      }

      // When
      await client.patch(path, body, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        method: 'PATCH',
        body: '{"key":"value"}',
      })
    })

    it('should have default value for data', async () => {
      // Given
      const path = '/users/tuto-seen'

      // When
      await client.patch(path, undefined, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        method: 'PATCH',
        body: '{}',
      })
    })
  })

  describe('delete', () => {
    it('should call API with given path and JSON Mime type and credentials by default and correct method', async () => {
      // Given
      const path = '/stocks/123'

      // When
      await client.delete(path)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        credentials: 'include',
        method: 'DELETE',
      })
    })

    it('should call API without credentials when not required', async () => {
      // Given
      const path = '/stocks/123'

      // When
      await client.delete(path, false)

      // Then
      expect(fetch).toHaveBeenCalledWith(`${API_URL}${path}`, {
        method: 'DELETE',
      })
    })

    it('should return json if return status is ok', async () => {
      // Given
      fetch.mockResponseOnce(JSON.stringify({ id: '123' }), { status: 200 })

      // When
      const response = await client.delete('/stocks/123')

      // Then
      expect(response.id).toBe('123')
    })
  })
})
