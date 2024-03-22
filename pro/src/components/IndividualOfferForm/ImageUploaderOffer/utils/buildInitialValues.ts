import { UploadImageValues } from 'components/ImageUploader/ButtonImageEdit/types'
import { IndividualOfferImage } from 'core/Offers/types'

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
