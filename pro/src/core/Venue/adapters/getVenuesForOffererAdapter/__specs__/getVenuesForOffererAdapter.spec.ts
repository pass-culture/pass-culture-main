import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { ALL_OFFERERS } from 'core/Offers'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

import getVenuesForOffererAdapter from '../getVenuesForOffererAdapter'

jest.mock('apiClient/api', () => ({
  api: {
    getVenues: jest.fn(),
  },
}))

describe('getVenuesForOffererAdapter', () => {
  beforeAll(() => {
    jest.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  })

  it('should call getVenues with good query params', async () => {
    await getVenuesForOffererAdapter({
      offererId: ALL_OFFERERS,
      activeOfferersOnly: false,
    })
    expect(api.getVenues).toHaveBeenCalledWith(
      false,
      undefined,
      false,
      undefined
    )

    await getVenuesForOffererAdapter({
      activeOfferersOnly: true,
    })
    expect(api.getVenues).toHaveBeenCalledWith(true, undefined, true, undefined)

    await getVenuesForOffererAdapter({ offererId: 'A1' })
    expect(api.getVenues).toHaveBeenCalledWith(false, undefined, false, 'A1')
  })

  it('should return error payload when api call fails', async () => {
    jest
      .spyOn(api, 'getVenues')
      .mockRejectedValueOnce(
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
