import { IndividualOfferImage } from '@/commons/core/Offers/types'
import { UploadImageValues } from '@/commons/utils/imageUploadTypes'
import { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

export const buildInitialValues = (
  imageOffer?: IndividualOfferImage | OnImageUploadArgs
): UploadImageValues => {
  const defaultInitialValues = {
    croppedImageUrl: '',
    credit: '',
    cropParams: {
      xCropPercent: 1,
      yCropPercent: 1,
      heightCropPercent: 0,
      widthCropPercent: 0,
    },
  }

  if (!imageOffer) {
    return defaultInitialValues
  }

  // Image is still a draft at this point.
  // Therefore, it's a OnImageUploadArgs type.
  if ('imageFile' in imageOffer) {
    return {
      croppedImageUrl: imageOffer.imageCroppedDataUrl ?? '',
      credit: imageOffer.credit ?? '',
      cropParams: {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    }
  }

  // Image has been uploaded once.
  // Therefore, it's a IndividualOfferImage type.
  if ('url' in imageOffer) {
    return {
      croppedImageUrl: imageOffer.url,
      credit: imageOffer.credit ?? '',
      cropParams: imageOffer.cropParams ?? {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    }
  }

  return defaultInitialValues
}
