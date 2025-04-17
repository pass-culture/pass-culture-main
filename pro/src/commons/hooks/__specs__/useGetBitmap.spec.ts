import { renderHook, waitFor } from '@testing-library/react'

import { useGetImageBitmap } from 'commons/hooks/useGetBitmap'
import * as imageUtils from 'commons/utils/image'

describe('useGetImageBitmap', () => {
  it('should return width and height of provided file', async () => {
    const mockedWidth = 600
    const mockedHeight = 800

    vi.spyOn(imageUtils, 'getImageBitmap').mockResolvedValue({
      width: mockedWidth,
      height: mockedHeight,
    } as ImageBitmap)
    const imageFile = new File([''], 'hello.png', {
      type: 'image/png',
    })
    Object.defineProperty(imageFile, 'size', {
      value: 9000000,
      configurable: true,
    })
    Object.defineProperty(imageFile, 'width', {
      value: mockedWidth,
      configurable: true,
    })
    Object.defineProperty(imageFile, 'height', {
      value: mockedHeight,
      configurable: true,
    })
    const { result } = renderHook(() => useGetImageBitmap(imageFile))
    const image = result.current

    expect(image.width).toEqual(0)
    expect(image.height).toEqual(0)

    await waitFor(() => {
      expect(result.current.width).toEqual(mockedWidth)
      expect(result.current.height).toEqual(mockedHeight)
    })
  })

  it('should return 0 width and height if no file is provided', () => {
    const { result } = renderHook(() => useGetImageBitmap())
    const image = result.current

    expect(image.width).toEqual(0)
    expect(image.height).toEqual(0)
  })
})
