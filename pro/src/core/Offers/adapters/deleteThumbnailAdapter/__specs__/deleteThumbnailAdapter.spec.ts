import { api } from 'apiClient/api'

import deleteThumbnailAdapter from '../deleteThumbnailAdapter'

describe('test deleteThumbnailAdapter', () => {
  let offerId: number

  beforeEach(() => {
    offerId = 12
  })
  it('should return success on api call success', async () => {
    vi.spyOn(api, 'deleteThumbnail').mockResolvedValue(undefined)
    const response = await deleteThumbnailAdapter(offerId)
    expect(response.isOk).toBeTruthy()
  })
  it('should return error on api call error', async () => {
    vi.spyOn(api, 'deleteThumbnail').mockRejectedValue(undefined)
    const response = await deleteThumbnailAdapter(offerId)
    expect(response.isOk).toBeFalsy()
  })
})
