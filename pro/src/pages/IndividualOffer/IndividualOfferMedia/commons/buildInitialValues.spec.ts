import { IndividualOfferImage } from '@/commons/core/Offers/types'
import { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

import { buildInitialValues } from './buildInitialValues'

describe('test ImageUploader:utils:buildInitialValues', () => {
  it('should build default initial values', () => {
    const initialValues = buildInitialValues()
    expect(initialValues).toEqual({
      croppedImageUrl: '',
      credit: '',
      cropParams: {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    })
  })

  it('should build initial values for previously saved image', () => {
    const imageOffer: IndividualOfferImage = {
      url: 'https://test.url',
      credit: 'John Do',
      cropParams: {
        xCropPercent: 0.5,
        yCropPercent: 0.5,
        heightCropPercent: 0.5,
        widthCropPercent: 0.5,
      },
    }
    const initialValues = buildInitialValues(imageOffer)
    expect(initialValues).toEqual({
      croppedImageUrl: imageOffer.url,
      credit: imageOffer.credit,
      cropParams: {
        xCropPercent: 0.5,
        yCropPercent: 0.5,
        heightCropPercent: 0.5,
        widthCropPercent: 0.5,
      },
    })
  })

  it('should build initial values for uploaded image', () => {
    const imageOffer: OnImageUploadArgs = {
      imageFile: new File([''], 'test.jpg'),
      imageCroppedDataUrl: 'https://cropped.test.url',
      cropParams: {
        x: 0.5,
        y: 0.5,
        width: 100,
        height: 100,
      },
      credit: 'John Do',
    }
    const initialValues = buildInitialValues(imageOffer)
    expect(initialValues).toEqual({
      croppedImageUrl: imageOffer.imageCroppedDataUrl,
      credit: imageOffer.credit,
      cropParams: {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    })
  })
})
