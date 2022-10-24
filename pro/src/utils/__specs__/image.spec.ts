import { getImageBitmap } from '../image'

describe('image', () => {
  it('GetImageBitmap', async () => {
    const imageFile = new File([''], 'hello.png', {
      type: 'image/png',
    })
    Object.defineProperty(imageFile, 'size', {
      value: 9000000,
      configurable: true,
    })
    Object.defineProperty(imageFile, 'width', {
      value: 600,
      configurable: true,
    })
    const bitmapImage = await getImageBitmap(imageFile)
    expect(bitmapImage?.width).toEqual(600)
  })
})
