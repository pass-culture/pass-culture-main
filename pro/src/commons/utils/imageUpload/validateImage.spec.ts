import { imageFileFactory } from '@/commons/utils/factories/imageUploadArgsFactories'

import { getImageDimensions } from './getImageDimensions'
import { getImageConditionsText, validateImage } from './validateImage'

vi.mock('./getImageDimensions', () => ({
  getImageDimensions: vi.fn(),
}))

const MIN_SIZES = { width: 400, height: 600 }

describe('validateImage', () => {
  it('should return the image with its dimensions', async () => {
    vi.mocked(getImageDimensions).mockResolvedValue({ width: 400, height: 600 })

    const { image, error } = await validateImage(
      imageFileFactory('image.jpg'),
      MIN_SIZES
    )

    expect(error).toBeUndefined()
    expect(image).toBeInstanceOf(File)
    expect(image).toMatchObject({
      name: 'image.jpg',
      type: 'image/jpeg',
      width: 400,
      height: 600,
    })
  })

  it.each([
    {
      case: 'the content is not an image',
      file: new File(['not an image'], 'image.jpg', { type: 'image/jpeg' }),
      dimensions: { width: 400, height: 600 },
      error: 'Le format de l’image n’est pas valide',
    },
    {
      case: 'the resolution is too large',
      file: imageFileFactory('image.jpg'),
      dimensions: { width: 10_000, height: 9000 },
      error:
        "Image trop volumineuse. La résolution maximale acceptée est d'environ 80 millions de pixels (9000 x 9000 pixels)",
    },
    {
      case: 'the image is too narrow',
      file: imageFileFactory('image.jpg'),
      dimensions: { width: 399, height: 600 },
      error:
        'L’image doit faire au moins 400 pixels de large et 600 pixels de haut',
    },
    {
      case: 'the image is too short',
      file: imageFileFactory('image.jpg'),
      dimensions: { width: 400, height: 599 },
      error:
        'L’image doit faire au moins 400 pixels de large et 600 pixels de haut',
    },
  ])(
    'should return an error when $case',
    async ({ file, dimensions, error }) => {
      vi.mocked(getImageDimensions).mockResolvedValue(dimensions)

      expect(await validateImage(file, MIN_SIZES)).toEqual({ error })
    }
  )

  it('should not check the minimum dimensions when there are none', async () => {
    vi.mocked(getImageDimensions).mockResolvedValue({ width: 1, height: 1 })

    const { error } = await validateImage(imageFileFactory('image.jpg'))

    expect(error).toBeUndefined()
  })

  it('should return a format error when the image cannot be read', async () => {
    vi.mocked(getImageDimensions).mockRejectedValue(
      new Error("Impossible de lire l'image")
    )

    expect(await validateImage(imageFileFactory('image.jpg'))).toEqual({
      error: 'Le format de l’image n’est pas valide',
    })
  })
})

describe('getImageConditionsText', () => {
  it('should list the accepted formats, the maximum weight and the maximum resolution', () => {
    expect(getImageConditionsText()).toBe(
      'Formats acceptés : JPEG, JPG, PNG, MPO, WEBP. Poids maximum : 10 Mo. Résolution maximale : 80 mégapixels.'
    )
  })

  it('should add the minimum dimensions', () => {
    expect(getImageConditionsText(MIN_SIZES)).toBe(
      'Formats acceptés : JPEG, JPG, PNG, MPO, WEBP. Poids maximum : 10 Mo. Résolution maximale : 80 mégapixels. Largeur minimale : 400 px. Hauteur minimale : 600 px.'
    )
  })
})
