import { renderHook, waitFor } from '@testing-library/react'

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
    const { result } = renderHook(() => useGetImageBitmap(imageFile))
    const image = result.current

    expect(image.width).toEqual(0)
    expect(image.height).toEqual(0)

    await waitFor(() => {
      expect(result.current.width).toEqual(600)
      expect(result.current.height).toEqual(800)
    })
  })
})
