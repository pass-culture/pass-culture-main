import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import { URL_FOR_MAINTENANCE } from '@/commons/utils/config'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('Maintenance', () => {
  const mockLocationAssign = vi.fn()

  beforeEach(() => {
    vi.spyOn(window, 'location', 'get').mockReturnValue({
      ...window.location,
      assign: mockLocationAssign,
    })
  })

  it('should redirect to maintenance page api v1 responds with status 503', async () => {
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    await api.getBookingsPro()

    expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })

  it('should redirect to maintenance page api v2 responds with status 503', async () => {
    fetchMock.mockResponse('Service Unavailable', { status: 503 })

    await api.getBookingByToken('')

    expect(mockLocationAssign).toHaveBeenCalledWith(URL_FOR_MAINTENANCE)
  })
})
