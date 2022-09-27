import { buildInitialValues } from '../buildInitialValues'

describe('test ImageUploader:utils:buildInitialValues', () => {
  it('should build default initial values', () => {
    const initialValues = buildInitialValues()
    expect(initialValues).toEqual({
      originalImageUrl: '',
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
    const inputData = {
      imageUrl: 'http://test.url',
      credit: 'John Do',
    }
    const initialValues = buildInitialValues(...Object.values(inputData))
    expect(initialValues).toEqual({
      imageUrl: inputData.imageUrl,
      originalImageUrl: inputData.imageUrl,
      credit: inputData.credit,
      cropParams: {
        xCropPercent: 1,
        yCropPercent: 1,
        heightCropPercent: 0,
        widthCropPercent: 0,
      },
    })
  })
})
