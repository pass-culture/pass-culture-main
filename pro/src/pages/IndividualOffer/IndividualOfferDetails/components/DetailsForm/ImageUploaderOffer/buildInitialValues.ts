import { IndividualOfferImage } from 'commons/core/Offers/types'
import { UploadImageValues } from 'commons/utils/imageUploadTypes'

export const buildInitialValues = (
  imageOffer?: IndividualOfferImage
): UploadImageValues => {
  return {
    imageUrl: imageOffer?.url || '',
    originalImageUrl: imageOffer?.originalUrl || '',
    credit: imageOffer?.credit || '',
    cropParams: imageOffer?.cropParams || {
      xCropPercent: 1,
      yCropPercent: 1,
      heightCropPercent: 0,
      widthCropPercent: 0,
    },
  }
}
