import { act, renderHook } from '@testing-library/react'

import { api } from '@/apiClient//api'
import { useIndividualOfferImageUpload } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/useIndividualOfferImageUpload'

vi.mock('@/apiClient//api', () => ({
  api: {
    createThumbnail: vi.fn(),
    deleteThumbnail: vi.fn(),
  },
}))

const MOCK_DATA = {
  initialImage: {
    url: 'initialImage.jpg',
    originalUrl: 'initialImage.jpg',
    credit: 'initial credit',
    cropParams: {
      xCropPercent: 0,
      yCropPercent: 0,
      heightCropPercent: 0,
      widthCropPercent: 0,
    },
  },
}

describe('useIndividualOfferImageUpload', () => {
  it('should return the initial image offer as displayed image at first', () => {
    const { result } = renderHook(() =>
      useIndividualOfferImageUpload(MOCK_DATA.initialImage)
    )

    expect(result.current.displayedImage).toEqual(MOCK_DATA.initialImage)
  })

  it('should return nothing as displayed image at first if no initial image was provided', () => {
    const { result } = renderHook(() => useIndividualOfferImageUpload())

    expect(result.current.displayedImage).toEqual(undefined)
  })

  it('should return nothing as displayed image if the initial image is to be deleted', () => {
    const { result } = renderHook(() =>
      useIndividualOfferImageUpload(MOCK_DATA.initialImage)
    )

    act(() => {
      result.current.onImageDelete()
    })

    expect(result.current.displayedImage).toEqual(undefined)
  })

  it('should return the new image as displayed image after upload', () => {
    const { result } = renderHook(() => useIndividualOfferImageUpload())

    const newImage = {
      imageFile: new File([''], 'test.jpg'),
      imageCroppedDataUrl: 'https://cropped.test.url',
      cropParams: {
        x: 0.5,
        y: 0.5,
        width: 100,
        height: 100,
      },
      credit: 'John Do',
    }

    act(() => {
      result.current.onImageUpload(newImage)
    })

    expect(result.current.displayedImage).toEqual(newImage)
  })

  it('should return ean image as displayed image after a prefill (handleEanImage(url))', () => {
    const { result } = renderHook(() => useIndividualOfferImageUpload())

    const eanImageUrl = 'eanImage.jpg'

    act(() => {
      result.current.handleEanImage(eanImageUrl)
    })

    expect(result.current.displayedImage).toEqual({
      credit: null,
      url: eanImageUrl,
    })
  })

  it('should return nothing as displayed image after a prefilled-by-ean reset (handleEanImage(undefined)', () => {
    const { result } = renderHook(() => useIndividualOfferImageUpload())

    const eanImageUrl = 'eanImage.jpg'

    act(() => {
      result.current.handleEanImage(eanImageUrl)
    })

    act(() => {
      result.current.handleEanImage(undefined)
    })

    expect(result.current.displayedImage).toEqual(undefined)
  })

  it('should call createThumbnail when a new image is uploaded', async () => {
    const { result } = renderHook(() =>
      useIndividualOfferImageUpload(MOCK_DATA.initialImage)
    )

    const newImage = {
      imageFile: new File([''], 'test.jpg'),
      imageCroppedDataUrl: 'https://cropped.test.url',
      cropParams: {
        x: 0.5,
        y: 0.5,
        width: 100,
        height: 100,
      },
      credit: 'John Do',
    }

    act(() => {
      result.current.onImageUpload(newImage)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(1)
    })

    expect(api.createThumbnail).toHaveBeenCalledOnce()
  })

  it('should call deleteThumbnail when the image is deleted', async () => {
    const { result } = renderHook(() =>
      useIndividualOfferImageUpload(MOCK_DATA.initialImage)
    )

    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(1)
    })

    expect(api.deleteThumbnail).toHaveBeenCalledOnce()
  })
})
