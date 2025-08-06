import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import { URL_FOR_MAINTENANCE } from '@/commons/utils/config'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('Maintenance', () => {
  it('should redirect to maintenance page api v1 responds with status 503', async () => {
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    const mockLocationAssign = vi.fn()
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
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    const mockLocationAssign = vi.fn()
    Object.defineProperty(window, 'location', {
      value: {
        assign: mockLocationAssign,
      },
      configurable: true,
      enumerable: true,
      writable: true,
    })
    await api.getBookingByToken('')

    expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })
})
