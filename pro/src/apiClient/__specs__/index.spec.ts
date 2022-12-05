import '@testing-library/jest-dom'
import fetch from 'jest-fetch-mock'

import { api, apiContremarque } from 'apiClient/api'
import { URL_FOR_MAINTENANCE } from 'utils/config'

describe('Maintenance', () => {
  it('should redirect to maintenance page api v1 responds with status 503', async () => {
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
    await api.getBookingsPro()

    expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })

  it('should redirect to maintenance page api v2 responds with status 503', async () => {
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
    await apiContremarque.getBookingByTokenV2('')

    expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })
})
