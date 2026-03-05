import { buildInitialVenueImageValues } from './buildInitialVenueImageValues'

describe('buildInitialVenueImageValues', () => {
  it('should return undefined croppedImageUrl and originalImageUrl when bannerUrl and bannerMeta are not provided', () => {
    const result = buildInitialVenueImageValues()
    expect(result.croppedImageUrl).toBeUndefined()
    expect(result.originalImageUrl).toBeUndefined()
    expect(result.cropParams).toBeUndefined()
    expect(result.credit).toBe('')
  })

  it('should return correct values when bannerUrl and bannerMeta are provided', () => {
    const bannerUrl = 'https://example.com/banner.jpg'
    const bannerMeta = {
      original_image_url: 'https://example.com/original.jpg',
      crop_params: {
        x_crop_percent: 10,
        y_crop_percent: 20,
        height_crop_percent: 30,
        width_crop_percent: 40,
      },
      image_credit: 'Photo by John Doe',
    }

    const result = buildInitialVenueImageValues(bannerUrl, bannerMeta)

    expect(result.croppedImageUrl).toBe(bannerUrl)
    expect(result.originalImageUrl).toBe(bannerMeta.original_image_url)
    expect(result.cropParams).toEqual({
      xCropPercent: bannerMeta.crop_params.x_crop_percent,
      yCropPercent: bannerMeta.crop_params.y_crop_percent,
      heightCropPercent: bannerMeta.crop_params.height_crop_percent,
      widthCropPercent: bannerMeta.crop_params.width_crop_percent,
    })
    expect(result.credit).toBe(bannerMeta.image_credit)
  })

  it('should return default values when bannerMeta is provided without crop_params and image_credit', () => {
    const bannerUrl = 'https://example.com/banner.jpg'
    const bannerMeta = {
      original_image_url: 'https://example.com/original.jpg',
    }

    const result = buildInitialVenueImageValues(bannerUrl, bannerMeta)

    expect(result.croppedImageUrl).toBe(bannerUrl)
    expect(result.originalImageUrl).toBe(bannerMeta.original_image_url)
    expect(result.cropParams).toEqual({
      xCropPercent: 0,
      yCropPercent: 0,
      heightCropPercent: 0,
      widthCropPercent: 0,
    })
    expect(result.credit).toBe('')
  })

  it('should return undefined croppedImageUrl and originalImageUrl when bannerUrl is null and bannerMeta is null', () => {
    const result = buildInitialVenueImageValues(null, null)
    expect(result.croppedImageUrl).toBeUndefined()
    expect(result.originalImageUrl).toBeUndefined()
    expect(result.cropParams).toEqual({
      heightCropPercent: 0,
      widthCropPercent: 0,
      xCropPercent: 0,
      yCropPercent: 0,
    })
    expect(result.credit).toBe('')
  })
})
