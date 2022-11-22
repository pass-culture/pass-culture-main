import { IOnImageUploadArgs } from '../ModalImageEdit'

export const imageUploadArgsFactory = (): IOnImageUploadArgs => ({
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
