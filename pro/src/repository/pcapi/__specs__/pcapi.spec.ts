import { postThumbnail } from 'repository/pcapi/pcapi'
import { client } from 'repository/pcapi/pcapiClient'

vi.mock('repository/pcapi/pcapiClient', () => ({
  client: {
    delete: vi.fn(),
    get: vi.fn().mockResolvedValue({}),
    patch: vi.fn(),
    post: vi.fn().mockResolvedValue({}),
    postWithFormData: vi.fn(),
  },
}))

vi.mock('utils/date', async () => {
  return {
    ...(await vi.importActual('utils/date')),
    getToday: vi.fn(() => new Date(2020, 8, 12)),
  }
})

describe('pcapi', () => {
  describe('postThumbnail', () => {
    it('should call the api correct POST route with thumbnail info as body param', async () => {
      const file = new File([''], 'myThumb.png')
      const body = new FormData()
      body.append('offerId', 'AA')
      body.append('thumb', file)
      body.append('credit', 'Mon crédit')
      body.append('croppingRectX', '12')
      body.append('croppingRectY', '32')
      body.append('croppingRectHeight', '350')
      body.append('croppingRectWidth', '220')
      body.append('thumbUrl', '')

      await postThumbnail('AA', file, 'Mon crédit', '', 12, 32, 350, 220)

      expect(client.postWithFormData).toHaveBeenCalledWith(
        `/offers/thumbnails`,
        body
      )
    })
  })
})
