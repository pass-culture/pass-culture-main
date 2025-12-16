import { type Mock, vi } from 'vitest'

import { api } from '@/apiClient/api'
import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'

import type { OfferEducationalFormValues } from '../../types'
import { postCollectiveOfferImage } from '../postCollectiveOfferImage'

vi.mock('@/apiClient/api', () => ({
  api: {
    attachOfferImage: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const snackBarSuccess = vi.fn()

describe('postCollectiveOfferImage', () => {
  const mockId = 123
  const imageUrl = 'https://example.com/image.jpg'
  const contentType = 'image/jpeg'
  const mockSnackBar = {
    error: snackBarError,
    success: snackBarSuccess,
  }

  const getInitialValues = (
    imageUrlValue: string
  ): OfferEducationalFormValues => ({
    ...getDefaultEducationalValues(),
    title: 'Test',
    description: 'Test description',
    offererId: '1',
    venueId: '1',
    imageUrl: imageUrlValue,
  })

  const createMockResponse = (blobResult: Blob | Error) => ({
    ok: true,
    headers: {
      get: vi.fn((header: string) =>
        header === 'content-type' ? contentType : null
      ),
    },
    blob:
      blobResult instanceof Error
        ? vi.fn().mockRejectedValue(blobResult)
        : vi.fn().mockResolvedValue(blobResult),
  })

  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should show error when fetch fails', async () => {
    ;(global.fetch as Mock).mockRejectedValue(new Error('Network error'))

    await postCollectiveOfferImage({
      initialValues: getInitialValues(imageUrl),
      snackBar: mockSnackBar,
      id: mockId,
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de récupérer votre image'
    )
    expect(api.attachOfferImage).not.toHaveBeenCalled()
  })

  it('should show error when blob() fails', async () => {
    const mockResponse = createMockResponse(new Error('Blob error'))
    ;(global.fetch as Mock).mockResolvedValue(mockResponse)

    await postCollectiveOfferImage({
      initialValues: getInitialValues(imageUrl),
      snackBar: mockSnackBar,
      id: mockId,
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de récupérer votre image'
    )
    expect(api.attachOfferImage).not.toHaveBeenCalled()
  })

  it('should show error when attachOfferImage fails', async () => {
    const mockBlob = new Blob(['image data'], { type: contentType })
    const mockResponse = createMockResponse(mockBlob)
    ;(global.fetch as Mock).mockResolvedValue(mockResponse)
    vi.spyOn(api, 'attachOfferImage').mockRejectedValue(new Error('API error'))

    await postCollectiveOfferImage({
      initialValues: getInitialValues(imageUrl),
      snackBar: mockSnackBar,
      id: mockId,
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Impossible de récupérer votre image'
    )
  })
})
