import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { hardRefresh } from '@/commons/utils/hardRefresh'

describe('hardRefresh', () => {
  const originalLocation = window.location

  beforeEach(() => {
    // Mock window.location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { href: '' },
    })
  })

  afterEach(() => {
    // Restore window.location
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    })
  })

  it('should set window.location.href with the provided URL', () => {
    const url = '/nouvelle-page'

    hardRefresh(url)

    expect(window.location.href).toBe(url)
  })

  it('should work with an absolute URL', () => {
    const url = 'https://example.com/page'

    hardRefresh(url)

    expect(window.location.href).toBe(url)
  })
})
