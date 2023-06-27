import { useCallback, useState } from 'react'

import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import deleteCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferImageAdapter'
import deleteCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/deleteCollectiveOfferTemplateImageAdapter'
import postCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferImageAdapter'
import postCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateImageAdapter'
import { OfferCollectiveImage } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'

export const useCollectiveOfferImageUpload = (
  offer?: CollectiveOffer | CollectiveOfferTemplate,
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

  const onImageUpload = useCallback(async (image: OnImageUploadArgs) => {
    setImageToUpload(image)
    setImageOffer({ url: image.imageCroppedDataUrl, credit: image.credit })
  }, [])

  const onImageDelete = useCallback(async () => {
    setImageToUpload(null)
    setImageOffer(null)
  }, [])

  const handleImageOnSubmit = useCallback(
    async (offerId: string) => {
      // Image field is empty
      if (imageOffer === null) {
        // Delete image if one was present before
        if (offer?.imageUrl === undefined || offer?.imageUrl === null) {
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

      const adapter = isTemplate
        ? postCollectiveOfferTemplateImageAdapter
        : postCollectiveOfferImageAdapter
      const { isOk, message, payload } = await adapter({
        offerId,
        imageFile: imageToUpload?.imageFile,
        credit: imageToUpload?.credit,
        cropParams: imageToUpload?.cropParams,
      })

      if (!isOk) {
        return notify.error(message)
      }
      setImageOffer({
        url: payload.imageUrl,
        credit: imageToUpload?.credit,
      })
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
