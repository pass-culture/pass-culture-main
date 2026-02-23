import { describe, expect, it, vi } from 'vitest'

import * as configModule from '@/commons/utils/config'

import { resizeImageURL } from '../resizeImageURL'

describe('resizeImageURL', () => {
  const mockImageURL = 'https://example.com/images/photo.jpg'

  beforeEach(() => {
    Object.defineProperty(window, 'devicePixelRatio', {
      value: 1,
      configurable: true,
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should return original URL when IMAGE_RESIZING_URL is not configured', () => {
    vi.spyOn(configModule, 'IMAGE_RESIZING_URL', 'get').mockReturnValue('')

    const result = resizeImageURL({ imageURL: mockImageURL, width: 300 })

    expect(result).toBe(mockImageURL)
  })

  it('should return original URL when in development', () => {
    vi.spyOn(configModule, 'IS_DEV', 'get').mockReturnValue(true)

    const result = resizeImageURL({ imageURL: mockImageURL, width: 300 })

    expect(result).toBe(mockImageURL)
  })

  it('should generate resized URL', () => {
    vi.spyOn(configModule, 'IMAGE_RESIZING_URL', 'get').mockReturnValue(
      'https://resize.example.com'
    )

    const result = resizeImageURL({ imageURL: mockImageURL, width: 300 })

    expect(result).toBe(
      'https://resize.example.com?size=300&filename=https://example.com/images/photo.jpg'
    )
  })

  it('should apply device pixel ratio', () => {
    vi.spyOn(configModule, 'IMAGE_RESIZING_URL', 'get').mockReturnValue(
      'https://resize.example.com'
    )
    Object.defineProperty(window, 'devicePixelRatio', {
      value: 2,
      configurable: true,
    })

    const result = resizeImageURL({ imageURL: mockImageURL, width: 300 })

    expect(result).toBe(
      'https://resize.example.com?size=600&filename=https://example.com/images/photo.jpg'
    )
  })
})
