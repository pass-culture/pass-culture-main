import { act, renderHook } from '@testing-library/react'

import { AttachImageResponseModel } from 'apiClient/v1'
import { imageUploadArgsFactory } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/__tests-utils__/imageUploadArgsFactory'
import * as deleteCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferImageAdapter'
import * as deleteCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferTemplateImageAdapter'
import * as postCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferImageAdapter'
import * as postCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateImageAdapter'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveOfferFactory,
  collectiveOfferTemplateFactory,
} from 'utils/collectiveApiFactories'

import { useCollectiveOfferImageUpload } from '../useCollectiveOfferImageUpload'

jest.mock('hooks/useNotification')
jest.mock('core/OfferEducational/adapters/postCollectiveOfferImageAdapter')
jest.mock(
  'core/OfferEducational/adapters/postCollectiveOfferTemplateImageAdapter'
)

const mockUseNotification = {
  close: vi.fn(),
  error: vi.fn(),
  pending: vi.fn(),
  information: vi.fn(),
  success: vi.fn(),
}

jest
  .spyOn(useNotification, 'default')
  .mockImplementation(() => mockUseNotification)

describe('useCollectiveOfferImageUpload', () => {
  it('should initialize with current image', async () => {
    const offer = collectiveOfferFactory()

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    expect(result.current.imageOffer?.url).toBe(offer.imageUrl)
  })

  it('should submit uploaded image in case of normal offer', async () => {
    const offer = collectiveOfferFactory()
    const image = imageUploadArgsFactory()
    const payload: AttachImageResponseModel = {
      imageUrl: 'https://example.com/image.jpg',
    }
    vi.spyOn(postCollectiveOfferImageAdapter, 'default').mockResolvedValue({
      isOk: true,
      payload,
      message: 'ok',
    })

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(postCollectiveOfferImageAdapter.default).toHaveBeenCalled()
  })

  it('should submit uploaded image in case of template offer', async () => {
    const offer = collectiveOfferTemplateFactory()
    const image = imageUploadArgsFactory()
    const payload: AttachImageResponseModel = {
      imageUrl: 'https://example.com/image.jpg',
    }
    jest
      .spyOn(postCollectiveOfferTemplateImageAdapter, 'default')
      .mockResolvedValue({
        isOk: true,
        payload,
        message: 'ok',
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

    expect(postCollectiveOfferTemplateImageAdapter.default).toHaveBeenCalled()
  })

  it('should delete image in case of normal offer', async () => {
    const offer = collectiveOfferTemplateFactory()
    vi.spyOn(deleteCollectiveOfferImageAdapter, 'default').mockResolvedValue({
      isOk: true,
      payload: null,
      message: 'ok',
    })

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(deleteCollectiveOfferImageAdapter.default).toHaveBeenCalled()
  })

  it('should delete image in case of template offer', async () => {
    const offer = collectiveOfferTemplateFactory()
    jest
      .spyOn(deleteCollectiveOfferTemplateImageAdapter, 'default')
      .mockResolvedValue({
        isOk: true,
        payload: null,
        message: 'ok',
      })

    const { result } = renderHook(() =>
      useCollectiveOfferImageUpload(offer, true)
    )
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(deleteCollectiveOfferTemplateImageAdapter.default).toHaveBeenCalled()
  })

  it('should not delete image if offer initially had one and onImageDelete was not called', async () => {
    const offer = collectiveOfferTemplateFactory()
    jest
      .spyOn(deleteCollectiveOfferTemplateImageAdapter, 'default')
      .mockResolvedValue({
        isOk: true,
        payload: null,
        message: 'ok',
      })

    const { result } = renderHook(() =>
      useCollectiveOfferImageUpload(offer, true)
    )

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(
      deleteCollectiveOfferTemplateImageAdapter.default
    ).not.toHaveBeenCalled()
  })
})
