import { describe, expect, it } from 'vitest'

import { formatPhoneNumber } from '../formatPhoneNumber'

describe('formatPhoneNumber', () => {
  it('should return formatted number in INTERNATIONAL format for +33618886536', () => {
    expect(formatPhoneNumber('+33618886536')).toBe('+33 6 18 88 65 36')
  })

  it('should return formatted number in NATIONAL format for +33618886536', () => {
    expect(formatPhoneNumber('+33618886536', 'NATIONAL')).toBe('06 18 88 65 36')
  })

  it('should return formatted number in INTERNATIONAL format for +262690886536', () => {
    expect(formatPhoneNumber('+262690886536')).toBe('+262 690 88 65 36')
  })

  it('should return formatted number in NATIONAL format for +262690886536', () => {
    expect(formatPhoneNumber('+262690886536', 'NATIONAL')).toBe('0690 88 65 36')
  })

  it('should return formatted number in INTERNATIONAL format for +508678912', () => {
    expect(formatPhoneNumber('+508678912')).toBe('+508 67 89 12')
  })

  it('should return formatted number in NATIONAL format for +508678912', () => {
    expect(formatPhoneNumber('+508678912', 'NATIONAL')).toBe('067 89 12')
  })

  it('should return empty string if given empty string', () => {
    expect(formatPhoneNumber('')).toBe('')
  })

  it('should return empty string if given null', () => {
    expect(formatPhoneNumber(null)).toBe('')
  })

  it('should return empty string if given undefined', () => {
    expect(formatPhoneNumber(undefined)).toBe('')
  })

  it('should return the input if non-phone input given', () => {
    expect(formatPhoneNumber('not a phone')).toBe('not a phone')
  })

  it('should not throw for malformed international phone and let as is', () => {
    expect(formatPhoneNumber('+444notanumber')).toBe('+444notanumber')
  })
})
