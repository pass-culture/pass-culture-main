import { useCallback, useState } from 'react'

import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { createThumbnailAdapter } from 'core/Offers/adapters/createThumbnailAdapter'
import { deleteThumbnailAdapter } from 'core/Offers/adapters/deleteThumbnailAdapter'
import { IndividualOfferImage } from 'core/Offers/types'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared'
import useNotification from 'hooks/useNotification'

import { imageFileToDataUrl } from '../InformationsScreen/utils/files'
import { getIndividualOfferImage } from '../utils/getIndividualOfferImage'

export const useIndividualOfferImageUpload = () => {
  const notify = useNotification()
  const { offerId, offer } = useIndividualOfferContext()

  const [imageOfferCreationArgs, setImageOfferCreationArgs] = useState<
    OnImageUploadArgs | undefined
  >(undefined)
  const [imageOffer, setImageOffer] = useState<
    IndividualOfferImage | undefined
  >(offer ? getIndividualOfferImage(offer) : undefined)

  const handleImageOnSubmit = useCallback(
    async (
      imageOfferId: number,
      imageEditionCreationArgs?: OnImageUploadArgs
    ) => {
      // Param is passed through state when the offer is not created yet and through param
      // in edition, which is not ideal. We should only have one flow here
      const creationArgs = imageOfferCreationArgs ?? imageEditionCreationArgs
      if (creationArgs === undefined) {
        return
      }
      const { imageFile, credit, cropParams } = creationArgs

      const response = await createThumbnailAdapter({
        offerId: imageOfferId,
        credit,
        imageFile,
        cropParams,
      })

      if (!response.isOk) {
        return Promise.reject()
      }

      setImageOffer({
        originalUrl: response.payload.url,
        url: response.payload.url,
        credit: response.payload.credit,
      })

      return Promise.resolve()
    },
    [imageOfferCreationArgs]
  )

  const onImageUpload = async ({
    imageFile,
    imageCroppedDataUrl,
    credit,
    cropParams,
  }: OnImageUploadArgs) => {
    const creationArgs = {
      imageFile,
      credit,
      cropParams,
    }
    if (offerId === null) {
      setImageOfferCreationArgs(creationArgs)
      imageFileToDataUrl(imageFile, (imageUrl) => {
        setImageOffer({
          originalUrl: imageUrl,
          url: imageCroppedDataUrl || imageUrl,
          credit,
          cropParams: cropParams
            ? {
                xCropPercent: cropParams.x,
                yCropPercent: cropParams.y,
                heightCropPercent: cropParams.height,
                widthCropPercent: cropParams.width,
              }
            : undefined,
        })
      })
    } else {
      try {
        await handleImageOnSubmit(offerId, creationArgs)
      } catch {
        notify.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const onImageDelete = async () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (!offerId) {
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOffer(undefined)
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOfferCreationArgs(undefined)
    } else {
      const response = await deleteThumbnailAdapter(offerId)
      if (response.isOk) {
        setImageOffer(undefined)
      } else {
        notify.error(response.message)
      }
    }
  }

  return {
    imageOffer,
    onImageUpload,
    onImageDelete,
    handleImageOnSubmit,
  }
}
