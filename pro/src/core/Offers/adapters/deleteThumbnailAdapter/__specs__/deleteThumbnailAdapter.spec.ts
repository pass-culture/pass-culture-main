import { api } from 'apiClient/api'

import deleteThumbnailAdapter from '../deleteThumbnailAdapter'

describe('test deleteThumbnailAdapter', () => {
  let offerId: string

  beforeEach(() => {
    offerId = 'AA'
  })
  it('should return success on api call success', async () => {
    jest.spyOn(api, 'deleteThumbnail').mockResolvedValue(undefined)
    const response = await deleteThumbnailAdapter({
      offerId,
    })
    expect(response.isOk).toBeTruthy()
  })
  it('should return error on api call error', async () => {
    jest.spyOn(api, 'deleteThumbnail').mockRejectedValue(undefined)
    const response = await deleteThumbnailAdapter({
      offerId,
    })
    expect(response.isOk).toBeFalsy()
  })
})
