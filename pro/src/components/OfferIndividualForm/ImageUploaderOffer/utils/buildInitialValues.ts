import { IUploadImageValues } from 'components/ImageUploader/ButtonImageEdit'
import { OfferIndividualImage } from 'core/Offers/types'

export const buildInitialValues = (
  imageOffer?: OfferIndividualImage
): IUploadImageValues => {
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
