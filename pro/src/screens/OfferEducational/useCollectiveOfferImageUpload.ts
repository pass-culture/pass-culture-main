import { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import deleteCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferImageAdapter'
import deleteCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferTemplateImageAdapter'
import { OfferCollectiveImage } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

export const useCollectiveOfferImageUpload = (
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel,
  isTemplate?: boolean
) => {
  const notify = useNotification()
  const [imageOffer, setImageOffer] = useState<OfferCollectiveImage | null>(
    offer !== undefined
      ? { url: offer.imageUrl, credit: offer.imageCredit }
      : null
  )
  const [imageToUpload, setImageToUpload] = useState<OnImageUploadArgs | null>(
    null
  )

  const onImageUpload = useCallback((image: OnImageUploadArgs) => {
    setImageToUpload(image)
    setImageOffer({ url: image.imageCroppedDataUrl, credit: image.credit })
  }, [])

  const onImageDelete = useCallback(() => {
    setImageToUpload(null)
    setImageOffer(null)
  }, [])

  const handleImageOnSubmit = useCallback(
    async (offerId: number) => {
      // Image field is empty
      if (imageOffer === null) {
        // Delete image if one was present before
        if (offer?.imageUrl === undefined || offer.imageUrl === null) {
          return
        }

        const adapter = isTemplate
          ? deleteCollectiveOfferTemplateImageAdapter
          : deleteCollectiveOfferImageAdapter

        const { isOk, message } = await adapter(offerId)
        if (!isOk) {
          notify.error(message)
        }

        return
      }

      // If imageOffer is not empty and imageToUpload is null
      // it means that the image was not changed
      if (imageToUpload === null) {
        return
      }

      try {
        const params = {
          thumb: imageToUpload.imageFile,
          credit: imageToUpload.credit ?? '',
          croppingRectHeight: imageToUpload.cropParams?.height ?? 0,
          croppingRectWidth: imageToUpload.cropParams?.width ?? 0,
          croppingRectX: imageToUpload.cropParams?.x ?? 0,
          croppingRectY: imageToUpload.cropParams?.y ?? 0,
        }

        const payload = isTemplate
          ? await api.attachOfferTemplateImage(offerId, params)
          : await api.attachOfferImage(offerId, params)
        setImageOffer({
          url: payload.imageUrl,
          credit: imageToUpload.credit,
        })
      } catch (error) {
        sendSentryCustomError(error)

        return notify.error(
          'Une erreur est survenue lors de l’envoi de votre image'
        )
      }
    },
    [imageOffer, imageToUpload]
  )

  return {
    imageOffer,
    onImageUpload,
    onImageDelete,
    handleImageOnSubmit,
  }
}
