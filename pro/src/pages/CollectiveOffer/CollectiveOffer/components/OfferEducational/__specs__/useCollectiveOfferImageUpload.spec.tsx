import { act, renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { Provider } from 'react-redux'

import { api } from '@/apiClient/api'
import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import { configureTestStore } from '@/commons/store/testUtils'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { imageUploadArgsFactory } from '@/commons/utils/factories/imageUploadArgsFactories'
import * as sendSentryCustomError from '@/commons/utils/sendSentryCustomError'

import { useCollectiveOfferImageUpload } from '../useCollectiveOfferImageUpload'

vi.mock('@/commons/hooks/useSnackBar')
vi.mock('@/commons/utils/sendSentryCustomError')

vi.mock('@/apiClient/api', () => ({
  api: {
    deleteOfferImage: vi.fn(),
    deleteOfferTemplateImage: vi.fn(),
    attachOfferImage: vi.fn(),
    attachOfferTemplateImage: vi.fn(),
  },
}))

const snackBarError = vi.fn()
const snackBarSuccess = vi.fn()
const sendSentryCustomErrorSpy = vi.fn()

vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
  error: snackBarError,
  success: snackBarSuccess,
}))

vi.spyOn(sendSentryCustomError, 'sendSentryCustomError').mockImplementation(
  sendSentryCustomErrorSpy
)

const renderUseCollectiveOfferImageUploadWrapper = ({
  offer,
  isTemplate = false,
}: {
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
  isTemplate?: boolean
}) => {
  const store = configureTestStore({})

  const wrapper = ({ children }: { children: ReactNode }) => (
    <Provider store={store}>{children}</Provider>
  )

  return renderHook(() => useCollectiveOfferImageUpload(offer, isTemplate), {
    wrapper,
  })
}

describe('useCollectiveOfferImageUpload', () => {
  it('should initialize with current image', () => {
    const offer = getCollectiveOfferFactory()

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
    expect(result.current.imageOffer?.url).toBe(offer.imageUrl)
  })

  it('should submit uploaded image in case of normal offer', async () => {
    const offer = getCollectiveOfferFactory()
    const image = imageUploadArgsFactory()
    vi.spyOn(api, 'attachOfferImage').mockResolvedValue({
      imageUrl: 'https://example.com/image.jpg',
    })

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
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

    const { result } = renderUseCollectiveOfferImageUploadWrapper({
      offer,
      isTemplate: true,
    })
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

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
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

    const { result } = renderUseCollectiveOfferImageUploadWrapper({
      offer,
      isTemplate: true,
    })
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

    const { result } = renderUseCollectiveOfferImageUploadWrapper({
      offer,
      isTemplate: true,
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferTemplateImage).not.toHaveBeenCalled()
  })

  it('should return early if imageOffer is null and offer had no image initially', async () => {
    const offer = getCollectiveOfferFactory({ imageUrl: null })

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferImage).not.toHaveBeenCalled()
    expect(snackBarError).not.toHaveBeenCalled()
  })

  it('should return early if imageOffer is null and offer imageUrl is undefined', async () => {
    const offer = getCollectiveOfferFactory({ imageUrl: undefined })

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.deleteOfferImage).not.toHaveBeenCalled()
    expect(snackBarError).not.toHaveBeenCalled()
  })

  it('should show error message when image deletion fails for normal offer', async () => {
    const offer = getCollectiveOfferFactory()
    vi.spyOn(api, 'deleteOfferImage').mockRejectedValue(
      new Error('Delete failed')
    )

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la suppression de l’image de l’offre'
    )
  })

  it('should show error message when image deletion fails for template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    vi.spyOn(api, 'deleteOfferTemplateImage').mockRejectedValue(
      new Error('Delete failed')
    )

    const { result } = renderUseCollectiveOfferImageUploadWrapper({
      offer,
      isTemplate: true,
    })
    act(() => {
      result.current.onImageDelete()
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la suppression de l’image de l’offre'
    )
  })

  it('should pass crop parameters when uploading image', async () => {
    const offer = getCollectiveOfferFactory()
    const image = imageUploadArgsFactory()
    image.credit = 'Test credit'
    image.cropParams = {
      x: 10,
      y: 20,
      width: 200,
      height: 300,
    }
    vi.spyOn(api, 'attachOfferImage').mockResolvedValue({
      imageUrl: 'https://example.com/image.jpg',
    })

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.attachOfferImage).toHaveBeenCalledWith(3, {
      thumb: image.imageFile,
      credit: 'Test credit',
      croppingRectHeight: 300,
      croppingRectWidth: 200,
      croppingRectX: 10,
      croppingRectY: 20,
    })
  })

  it('should use default values when crop params are missing', async () => {
    const offer = getCollectiveOfferFactory()
    const image = imageUploadArgsFactory()
    image.credit = ''
    image.cropParams = undefined
    vi.spyOn(api, 'attachOfferImage').mockResolvedValue({
      imageUrl: 'https://example.com/image.jpg',
    })

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(api.attachOfferImage).toHaveBeenCalledWith(3, {
      thumb: image.imageFile,
      credit: '',
      croppingRectHeight: 0,
      croppingRectWidth: 0,
      croppingRectX: 0,
      croppingRectY: 0,
    })
  })

  it('should send error to Sentry and show error message when image upload fails for normal offer', async () => {
    const offer = getCollectiveOfferFactory()
    const image = imageUploadArgsFactory()
    const error = new Error('Upload failed')
    vi.spyOn(api, 'attachOfferImage').mockRejectedValue(error)

    const { result } = renderUseCollectiveOfferImageUploadWrapper({ offer })
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(sendSentryCustomErrorSpy).toHaveBeenCalledWith(error)
    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’envoi de votre image'
    )
  })

  it('should send error to Sentry and show error message when image upload fails for template offer', async () => {
    const offer = getCollectiveOfferTemplateFactory()
    const image = imageUploadArgsFactory()
    const error = new Error('Upload failed')
    vi.spyOn(api, 'attachOfferTemplateImage').mockRejectedValue(error)

    const { result } = renderUseCollectiveOfferImageUploadWrapper({
      offer,
      isTemplate: true,
    })
    act(() => {
      result.current.onImageUpload(image)
    })

    await act(async () => {
      await result.current.handleImageOnSubmit(3)
    })

    expect(sendSentryCustomErrorSpy).toHaveBeenCalledWith(error)
    expect(snackBarError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de l’envoi de votre image'
    )
  })
})
