import {
  MAX_THUMBNAIL_WIDTH,
  MIN_COLLECTIVE_IMAGE_DIMENSIONS,
} from '@/components/ImageDragAndDrop/constants'

import { getImageBitmap } from '../image'
import { prepareImageForUpload } from '../prepareImageForUpload'

const { resize, toBlob } = vi.hoisted(() => ({
  resize: vi.fn(),
  toBlob: vi.fn(),
}))

vi.mock('pica', () => ({ default: () => ({ resize, toBlob }) }))
vi.mock('../image', () => ({ getImageBitmap: vi.fn() }))

describe('prepareImageForUpload', () => {
  const file = new File(['original image'], 'photo.jpg', {
    type: 'image/jpeg',
    lastModified: 123,
  })
  const close = vi.fn()

  beforeEach(() => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 4000,
      height: 3000,
      close,
    } as unknown as ImageBitmap)
    resize.mockImplementation(async (_source, canvas) => canvas)
    toBlob.mockResolvedValue(new Blob(['small'], { type: 'image/jpeg' }))
  })

  it('should reduce large images while preserving the file metadata', async () => {
    const result = await prepareImageForUpload(file)

    expect(result.size).toBeLessThan(file.size)
    expect(result.name).toBe(file.name)
    expect(result.type).toBe(file.type)
    expect(result.lastModified).toBe(file.lastModified)
    expect(resize).toHaveBeenCalledWith(
      expect.objectContaining({ width: 4000, height: 3000 }),
      expect.objectContaining({
        width: MAX_THUMBNAIL_WIDTH,
        height: 563,
      })
    )
    expect(toBlob).toHaveBeenCalledWith(
      resize.mock.calls[0][1],
      'image/jpeg',
      0.85
    )
    expect(close).toHaveBeenCalled()
  })

  it('should keep small images unchanged', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 400,
      height: 600,
      close,
    } as unknown as ImageBitmap)

    expect(await prepareImageForUpload(file)).toBe(file)
    expect(resize).not.toHaveBeenCalled()
  })

  it('should keep enough source pixels for the selected crop to reach the backend width', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 4000,
      height: 2000,
      close,
    } as unknown as ImageBitmap)

    await prepareImageForUpload(file, { cropWidth: 1 / 3 })

    expect(resize).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ width: 2250, height: 1125 })
    )
  })

  it.each([
    { width: 8000, height: 1200, expectedDimension: 4000 },
    { width: 800, height: 8000, expectedDimension: 7500 },
    { width: 7777, height: 1234, expectedDimension: 3782 },
  ])(
    'should preserve minimum dimensions for a $width by $height image',
    async ({ width, height, expectedDimension }) => {
      vi.mocked(getImageBitmap).mockResolvedValue({
        width,
        height,
        close,
      } as unknown as ImageBitmap)

      await prepareImageForUpload(file, {
        minSizes: MIN_COLLECTIVE_IMAGE_DIMENSIONS,
      })

      const canvas = resize.mock.calls[0][1] as HTMLCanvasElement
      expect(Math.max(canvas.width, canvas.height)).toBe(expectedDimension)
      expect(
        Math.floor((width * expectedDimension) / Math.max(width, height))
      ).toBeGreaterThanOrEqual(MIN_COLLECTIVE_IMAGE_DIMENSIONS.width)
      expect(
        Math.floor((height * expectedDimension) / Math.max(width, height))
      ).toBeGreaterThanOrEqual(MIN_COLLECTIVE_IMAGE_DIMENSIONS.height)
    }
  )

  it('should keep an image already at the minimum height unchanged', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 8000,
      height: 600,
      close,
    } as unknown as ImageBitmap)

    expect(
      await prepareImageForUpload(file, {
        minSizes: MIN_COLLECTIVE_IMAGE_DIMENSIONS,
      })
    ).toBe(file)
    expect(resize).not.toHaveBeenCalled()
  })

  it('should use the default minimum dimensions for individual offers', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 8000,
      height: 800,
      close,
    } as unknown as ImageBitmap)

    await prepareImageForUpload(file)

    expect(resize).toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ width: 4000, height: 400 })
    )
  })

  it('should not resize when the selected crop is already below the backend width', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue({
      width: 4000,
      height: 2000,
      close,
    } as unknown as ImageBitmap)

    expect(await prepareImageForUpload(file, { cropWidth: 0.1 })).toBe(file)
    expect(resize).not.toHaveBeenCalled()
  })

  it('should keep the original when crop width is invalid', async () => {
    expect(await prepareImageForUpload(file, { cropWidth: 0 })).toBe(file)
    expect(resize).not.toHaveBeenCalled()
  })

  it('should preserve the PNG format for transparent images', async () => {
    const png = new File(['original png image'], 'image.png', {
      type: 'image/png',
    })
    toBlob.mockResolvedValue(new Blob(['small'], { type: 'image/png' }))

    expect((await prepareImageForUpload(png)).type).toBe('image/png')
    expect(toBlob).toHaveBeenCalledWith(expect.anything(), 'image/png', 0.85)
  })

  it('should keep the original when compression produces a larger file', async () => {
    toBlob.mockResolvedValue(
      new File(['a compressed image larger than the original'], 'photo.jpg')
    )

    expect(await prepareImageForUpload(file)).toBe(file)
  })

  it('should keep the original when the image cannot be decoded', async () => {
    vi.mocked(getImageBitmap).mockResolvedValue(null)

    expect(await prepareImageForUpload(file)).toBe(file)
    expect(resize).not.toHaveBeenCalled()
  })

  it('should keep the original when the result is below the minimum dimensions', async () => {
    vi.mocked(getImageBitmap)
      .mockResolvedValueOnce({
        width: 4000,
        height: 3000,
        close,
      } as unknown as ImageBitmap)
      .mockResolvedValueOnce({
        width: 399,
        height: 600,
        close,
      } as unknown as ImageBitmap)

    expect(await prepareImageForUpload(file)).toBe(file)
  })

  it('should keep the original when the compressed image cannot be decoded', async () => {
    vi.mocked(getImageBitmap)
      .mockResolvedValueOnce({
        width: 4000,
        height: 3000,
        close,
      } as unknown as ImageBitmap)
      .mockResolvedValueOnce(null)

    expect(await prepareImageForUpload(file)).toBe(file)
  })

  it('should keep the original when compression fails', async () => {
    resize.mockRejectedValue(new Error('Resize failed'))

    expect(await prepareImageForUpload(file)).toBe(file)
    expect(close).toHaveBeenCalled()
  })

  it('should keep the source bitmap open until resizing completes', async () => {
    resize.mockImplementationOnce((_source, canvas) => {
      expect(close).not.toHaveBeenCalled()
      return Promise.resolve(canvas)
    })

    await prepareImageForUpload(file)

    expect(close).toHaveBeenCalled()
  })

  it('should keep the original when encoding fails', async () => {
    toBlob.mockRejectedValue(new Error('Encoding failed'))

    expect(await prepareImageForUpload(file)).toBe(file)
    expect(close).toHaveBeenCalled()
  })

  it('should keep the original when the browser changes the output format', async () => {
    toBlob.mockResolvedValue(new Blob(['small'], { type: 'image/png' }))

    expect(await prepareImageForUpload(file)).toBe(file)
  })

  it('should not process unsupported formats', async () => {
    const gif = new File(['gif'], 'image.gif', { type: 'image/gif' })

    expect(await prepareImageForUpload(gif)).toBe(gif)
    expect(getImageBitmap).not.toHaveBeenCalled()
    expect(resize).not.toHaveBeenCalled()
  })
})
