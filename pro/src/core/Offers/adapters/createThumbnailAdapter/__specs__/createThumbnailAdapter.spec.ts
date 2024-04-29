import { CroppedRect } from 'react-avatar-editor'

import { api } from 'apiClient/api'

import { createThumbnailAdapter } from '../createThumbnailAdapter'

describe('test createThumbnailAdapter', () => {
  let offerId: number
  let imageFile: File
  let credit: string
  let cropParams: CroppedRect

  beforeEach(() => {
    offerId = 12
    imageFile = new File([''], 'hello.png')
    credit = 'John Do'
    cropParams = { x: 1, y: 1, width: 1, height: 1 }
  })
  it('should return success on api call success', async () => {
    vi.spyOn(api, 'createThumbnail').mockResolvedValue({
      id: 12,
      url: 'https://backend.image.url',
      credit: 'John Do',
    })
    const response = await createThumbnailAdapter({
      offerId,
      imageFile,
      credit,
      cropParams,
    })
    expect(response.isOk).toBeTruthy()
  })
  it('should return error on api call error', async () => {
    vi.spyOn(api, 'createThumbnail').mockRejectedValue(undefined)
    const response = await createThumbnailAdapter({
      offerId,
      imageFile,
      credit,
      cropParams,
    })
    expect(response.isOk).toBeFalsy()
  })
})
