import type { OnImageUploadArgs } from '@/components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'

const JPEG_SIGNATURE = [
  0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01,
]
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]

export const imageFileFactory = (
  name = 'test-image.jpg',
  format: 'jpeg' | 'png' = 'jpeg'
): File => {
  const signature = format === 'png' ? PNG_SIGNATURE : JPEG_SIGNATURE

  return new File([new Uint8Array(signature)], name, {
    type: `image/${format}`,
  })
}

export const imageUploadArgsFactory = (): OnImageUploadArgs => ({
  imageFile: new File([''], 'filename'),
  imageCroppedDataUrl: 'https://example.com/image.jpg',
  credit: 'Best photographer ever',
  cropParams: {
    x: 0,
    y: 100,
    width: 100,
    height: 100,
  },
})
