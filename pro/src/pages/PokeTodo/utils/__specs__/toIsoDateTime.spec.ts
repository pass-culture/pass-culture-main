import { describe, expect, it } from 'vitest'

import { toIsoDatetime } from '../toIsoDatetime'

describe('toIsoDatetime', () => {
  it('returns null for null input', () => {
    expect(toIsoDatetime(null)).toBeNull()
  })

  it('returns null for empty string', () => {
    expect(toIsoDatetime('')).toBeNull()
  })

  it('appends :00Z to datetime-local value', () => {
    expect(toIsoDatetime('2026-12-31T23:59')).toBe('2026-12-31T23:59:00Z')
  })

  it('preserves value already ending with Z', () => {
    expect(toIsoDatetime('2026-12-31T23:59:00Z')).toBe('2026-12-31T23:59:00Z')
  })
})
