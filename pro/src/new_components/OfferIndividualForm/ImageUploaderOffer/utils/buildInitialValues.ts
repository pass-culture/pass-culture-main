import { IUploadImageValues } from 'new_components/ImageUploader/ButtonImageEdit'

export const buildInitialValues = (
  imageUrl?: string,
  credit?: string
): IUploadImageValues => {
  return {
    imageUrl,
    originalImageUrl: imageUrl || '',
    credit: credit || '',
    cropParams: {
      xCropPercent: 1,
      yCropPercent: 1,
      heightCropPercent: 0,
      widthCropPercent: 0,
    },
  }
}
