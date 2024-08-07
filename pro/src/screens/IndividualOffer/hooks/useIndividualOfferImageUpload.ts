import { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { OnImageUploadArgs } from 'components/ImageUploader/ButtonImageEdit/ModalImageEdit/ModalImageEdit'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import { IndividualOfferImage } from 'core/Offers/types'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import { useNotification } from 'hooks/useNotification'

import { imageFileToDataUrl } from '../InformationsScreen/utils/files'
import { getIndividualOfferImage } from '../utils/getIndividualOfferImage'

export const useIndividualOfferImageUpload = () => {
  const notify = useNotification()
  const { offer } = useIndividualOfferContext()

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

      const response = await api.createThumbnail({
        // TODO This TS error will be removed when spectree is updated to the latest
        // version (dependant on Flask update) which will include files in the generated schema
        // @ts-expect-error
        thumb: imageFile,
        credit: credit ?? '',
        croppingRectHeight: cropParams?.height,
        croppingRectWidth: cropParams?.width,
        croppingRectX: cropParams?.x,
        croppingRectY: cropParams?.y,
        offerId: imageOfferId,
      })

      setImageOffer({
        originalUrl: response.url,
        url: response.url,
        credit: response.credit ?? null,
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
    if (offer === null) {
      setImageOfferCreationArgs(creationArgs)
      const imageUrl = await imageFileToDataUrl(imageFile)
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
    } else {
      try {
        await handleImageOnSubmit(offer.id, creationArgs)
      } catch {
        notify.error(SENT_DATA_ERROR_MESSAGE)
      }
    }
  }

  const onImageDelete = async () => {
    /* istanbul ignore next: DEBT, TO FIX */
    if (!offer) {
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOffer(undefined)
      /* istanbul ignore next: DEBT, TO FIX */
      setImageOfferCreationArgs(undefined)
    } else {
      try {
        await api.deleteThumbnail(offer.id)
        setImageOffer(undefined)
      } catch {
        notify.error(
          'Une erreur est survenue lors de la suppression de votre image. Merci de réessayer plus tard.'
        )
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
