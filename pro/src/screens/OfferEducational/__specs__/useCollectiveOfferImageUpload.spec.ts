import { act, renderHook } from '@testing-library/react'

import { api } from 'apiClient/api'
import { imageUploadArgsFactory } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/__tests-utils__/imageUploadArgsFactory'
import * as useNotification from 'hooks/useNotification'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'

import { useCollectiveOfferImageUpload } from '../useCollectiveOfferImageUpload'

vi.mock('hooks/useNotification')

vi.mock('apiClient/api', () => ({
  api: {
    deleteOfferImage: vi.fn(),
    deleteOfferTemplateImage: vi.fn(),
    attachOfferImage: vi.fn(),
    attachOfferTemplateImage: vi.fn(),
  },
}))

const mockUseNotification = {
  close: vi.fn(),
  error: vi.fn(),
  pending: vi.fn(),
  information: vi.fn(),
  success: vi.fn(),
}

vi.spyOn(useNotification, 'useNotification').mockImplementation(
  () => mockUseNotification
)

describe('useCollectiveOfferImageUpload', () => {
  it('should initialize with current image', () => {
    const offer = getCollectiveOfferFactory()

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    expect(result.current.imageOffer?.url).toBe(offer.imageUrl)
  })

  it('should submit uploaded image in case of normal offer', async () => {
    const offer = getCollectiveOfferFactory()
    const image = imageUploadArgsFactory()
    vi.spyOn(api, 'attachOfferImage').mockResolvedValue({
      imageUrl: 'https://example.com/image.jpg',
    })

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.attachOfferImage).toHaveBeenCalled()
  })

  it('should submit uploaded image in case of template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    const image = imageUploadArgsFactory()
    vi.spyOn(api, 'attachOfferTemplateImage').mockResolvedValue({
      imageUrl: 'https://example.com/image.jpg',
    })

    const { result } = renderHook(() =>
      useCollectiveOfferImageUpload(offer, true)
    )
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.attachOfferTemplateImage).toHaveBeenCalled()
  })

  it('should delete image in case of normal offer', async () => {
    const offer = getCollectiveOfferFactory()

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferImage).toHaveBeenCalled()
  })

  it('should delete image in case of template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    const { result } = renderHook(() =>
      useCollectiveOfferImageUpload(offer, true)
    )
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferTemplateImage).toHaveBeenCalled()
  })

  it('should not delete image if offer initially had one and onImageDelete was not called', async () => {
    const offer = getCollectiveOfferTemplateFactory()

    const { result } = renderHook(() =>
      useCollectiveOfferImageUpload(offer, true)
    )

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferTemplateImage).not.toHaveBeenCalled()
  })
})
