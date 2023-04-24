import { IOfferIndividualImage } from 'core/Offers/types'

import { buildInitialValues } from '../buildInitialValues'

describe('test ImageUploader:utils:buildInitialValues', () => {
  it('should build default initial values', () => {
    const initialValues = buildInitialValues()
    expect(initialValues).toEqual({
      originalImageUrl: '',
      imageUrl: '',
      credit: '',
      cropParams: {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    })
  })
  it('should build initial values for given data', () => {
    const imageOffer: IOfferIndividualImage = {
      originalUrl: 'https://cropped.test.url',
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
      imageUrl: imageOffer.url,
      originalImageUrl: imageOffer.originalUrl,
      credit: imageOffer.credit,
      cropParams: {
        xCropPercent: 0.5,
        yCropPercent: 0.5,
        heightCropPercent: 0.5,
        widthCropPercent: 0.5,
      },
    })
  })
})
