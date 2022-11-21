import { useCallback, useState } from 'react'

import { IOnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import postCollectiveOfferImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferImageAdapter'
import postCollectiveOfferTemplateImageAdapter from 'core/OfferEducational/adapters/postCollectiveOfferTemplateImageAdapter'
import { IOfferCollectiveImage } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'

export const useImageUpload = (
  offer?: CollectiveOffer | CollectiveOfferTemplate,
  isTemplate?: boolean
) => {
  const notify = useNotification()
  const [imageOffer, setImageOffer] = useState<IOfferCollectiveImage | null>(
    offer !== undefined
      ? { url: offer.imageUrl, credit: offer.imageCredit }
      : null
  )
  const [imageToUpload, setImageToUpload] = useState<IOnImageUploadArgs | null>(
    null
  )

  const onImageUpload = useCallback(async (image: IOnImageUploadArgs) => {
    setImageToUpload(image)
    setImageOffer({ url: image.imageCroppedDataUrl, credit: image.credit })
  }, [])

  const onImageDelete = useCallback(async () => {
    setImageToUpload(null)
    setImageOffer(null)
  }, [])

  const handleImageOnSubmit = useCallback(
    async (offerId: string, isCreatingOffer = false) => {
      if (imageToUpload !== null) {
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
      } else {
        if (!isCreatingOffer) {
          // TODO delete image
        }
      }
    },
    [imageToUpload]
  )

  return {
    imageOffer,
    onImageUpload,
    onImageDelete,
    handleImageOnSubmit,
  }
}
