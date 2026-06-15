import { describe, expect, it } from 'vitest'

import { toStringOrNull } from '../toStringOrNull'

describe('toStringOrNull', () => {
  it("should trim text when it's non-empty", () => {
    expect(toStringOrNull(' a word ')).toBe('a word')
  })

  it('should return null when the text is empty', () => {
    expect(toStringOrNull('')).toBeNull()
    expect(toStringOrNull(' ')).toBeNull()
  })

  it('should return null the text is null', () => {
    expect(toStringOrNull(null)).toBeNull()
  })

  it('should return null the text is undefined', () => {
    expect(toStringOrNull(undefined)).toBeNull()
  })
})
