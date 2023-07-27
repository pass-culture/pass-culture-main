import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ALL_OFFERERS } from 'core/Offers/constants'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import getVenuesForOffererAdapter from '../getVenuesForOffererAdapter'

vi.mock('apiClient/api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))

describe('getVenuesForOffererAdapter', () => {
  beforeAll(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  })

  it('should call getVenues with good query params', async () => {
    await getVenuesForOffererAdapter({
      offererId: ALL_OFFERERS,
      activeOfferersOnly: false,
    })
    expect(api.getVenues).toHaveBeenCalledWith(undefined, false, undefined)

    await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    expect(api.getVenues).toHaveBeenCalledWith(undefined, true, undefined)

    const offererId = 10
    await getVenuesForOffererAdapter({ offererId: offererId.toString() })
    expect(api.getVenues).toHaveBeenCalledWith(undefined, false, offererId)
  })

  it('should return error payload when api call fails', async () => {
    vi.spyOn(api, 'getVenues').mockRejectedValueOnce(
      new ApiError({} as ApiRequestOptions, { status: 500 } as ApiResult, '')
    )

    const response = await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    expect(response.isOk).toBeFalsy()
    expect(response.message).toBe(GET_DATA_ERROR_MESSAGE)
    expect(response.payload).toStrictEqual([])
  })
})
