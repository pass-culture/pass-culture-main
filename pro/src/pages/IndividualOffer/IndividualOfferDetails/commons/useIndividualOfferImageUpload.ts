import { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

type IndividualImageOfferContextValues = {
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  hasUpsertedImage: boolean
  onImageUpload: (args: OnImageUploadArgs) => void
  onImageDelete: () => void
  handleEanImage: (imageUrl?: string) => void
  handleImageOnSubmit: (offerId: number) => Promise<void>
}

export const useIndividualOfferImageUpload = (
  initialImageOffer?: IndividualOfferImage
): IndividualImageOfferContextValues => {
  const [hasUpsertedImage, setHasUpsertedImage] = useState(false)
  const [imageOffer, setImageOffer] = useState<
    IndividualOfferImage | undefined
  >(initialImageOffer)
  const [imageToUpsert, setImageToUpsert] = useState<
    OnImageUploadArgs | undefined
  >(undefined)
  const displayedImage = hasUpsertedImage ? imageToUpsert : imageOffer

  const handleEanImage = useCallback((imageUrl?: string) => {
    if (imageUrl) {
      // There is nothing to upload, since the same image
      // will be used by offer based on a shared EAN.
      // We still need to set the image offer to be able to
      // display it as preview.
      setImageOffer({
        url: imageUrl,
        // Credit isn't defined in Product - images property,
        // is not needed for the preview anyway.
        credit: null,
      })
    } else {
      setImageOffer(undefined)
    }
  }, [])

  const handleImageOnSubmit = useCallback(
    async (offerId: number) => {
      const shouldUploadThumbnail = hasUpsertedImage && !!imageToUpsert
      const shouldDeleteThumbnail = hasUpsertedImage && !imageToUpsert

      if (shouldUploadThumbnail) {
        const { imageFile: thumb, credit, cropParams } = imageToUpsert
        const {
          height: croppingRectHeight,
          width: croppingRectWidth,
          x: croppingRectX,
          y: croppingRectY,
        } = cropParams ?? {}

        const thumbnail = {
          thumb,
          credit: credit ?? '',
          croppingRectHeight,
          croppingRectWidth,
          croppingRectX,
          croppingRectY,
          offerId,
        }

        await api.createThumbnail(thumbnail)
      } else if (shouldDeleteThumbnail) {
        await api.deleteThumbnail(offerId)
      }
    },
    [hasUpsertedImage, imageToUpsert]
  )

  const onImageUpload = useCallback((image: OnImageUploadArgs) => {
    setHasUpsertedImage(true)
    setImageToUpsert(image)
  }, [])

  const onImageDelete = useCallback(() => {
    setHasUpsertedImage(true)
    setImageToUpsert(undefined)
  }, [])

  return {
    displayedImage,
    hasUpsertedImage,
    onImageUpload,
    onImageDelete,
    handleEanImage,
    handleImageOnSubmit,
  }
}
