import { renderHook } from '@testing-library/react-hooks'

import { useGetImageBitmap } from 'hooks/useGetBitmap'

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
    Object.defineProperty(imageFile, 'height', {
      value: 800,
      configurable: true,
    })
    const { result, waitForNextUpdate } = renderHook(() =>
      useGetImageBitmap(imageFile)
    )
    const image = result.current

    expect(image.width).toEqual(0)
    expect(image.height).toEqual(0)

    await waitForNextUpdate()
    const updatedImage = result.current
    expect(updatedImage.width).toEqual(600)
    expect(updatedImage.height).toEqual(800)
  })
})
