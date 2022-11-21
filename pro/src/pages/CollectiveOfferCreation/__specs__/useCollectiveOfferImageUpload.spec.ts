import { act } from '@testing-library/react'
import { renderHook } from '@testing-library/react-hooks'

import { AttachImageResponseModel } from 'apiClient/v1'
import { imageUploadArgsFactory } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/__tests-utils__/imageUploadArgsFactory'
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
  close: jest.fn(),
  error: jest.fn(),
  pending: jest.fn(),
  information: jest.fn(),
  success: jest.fn(),
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
    jest.spyOn(postCollectiveOfferImageAdapter, 'default').mockResolvedValue({
      isOk: true,
      payload,
      message: 'ok',
    })

    const { result } = renderHook(() => useCollectiveOfferImageUpload(offer))
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit('someId', false)
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
      await result.current.handleImageOnSubmit('someId', false)
    })

    expect(postCollectiveOfferTemplateImageAdapter.default).toHaveBeenCalled()
  })
})
