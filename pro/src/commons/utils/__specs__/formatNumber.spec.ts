import { formatNumberLabel } from '../formatNumber'

describe('formatNumberLabel', () => {
  it('should format a number', () => {
    expect(formatNumberLabel(1000)).toBe('1\u202f000')
  })

  it('should add separators for large numbers', () => {
    expect(formatNumberLabel(1234567)).toBe('1\u202f234\u202f567')
  })

  it('should handle zero', () => {
    expect(formatNumberLabel(0)).toBe('0')
  })

  it('should handle negative numbers', () => {
    expect(formatNumberLabel(-1500)).toBe('-1\u202f500')
  })

  it('should return string', () => {
    expect(formatNumberLabel('Test')).toBe('Test')
  })
})
