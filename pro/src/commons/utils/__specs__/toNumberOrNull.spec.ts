import { toNumberOrNull } from '../toNumberOrNull'

describe('toNumberOrNull', () => {
  it('should return the same number when input is a number', () => {
    expect(toNumberOrNull(42)).toBe(42)
    expect(toNumberOrNull(0)).toBe(0)
    expect(toNumberOrNull(-7)).toBe(-7)
    expect(toNumberOrNull(3.14)).toBe(3.14)
  })

  it('should return null for null or undefined', () => {
    expect(toNumberOrNull(null)).toBeNull()
    expect(toNumberOrNull(undefined)).toBeNull()
  })

  it('should return null for empty or whitespace-only strings', () => {
    expect(toNumberOrNull('')).toBeNull()
    expect(toNumberOrNull('   ')).toBeNull()
    expect(toNumberOrNull('\n\t')).toBeNull()
  })

  it('should parse plain numeric strings', () => {
    expect(toNumberOrNull('12')).toBe(12)
    expect(toNumberOrNull('0')).toBe(0)
    expect(toNumberOrNull('-5')).toBe(-5)
    expect(toNumberOrNull('3.5')).toBe(3.5)
  })

  it('should parse numeric strings with surrounding spaces', () => {
    expect(toNumberOrNull(' 7 ')).toBe(7)
    expect(toNumberOrNull('  10.25  ')).toBe(10.25)
  })

  it('should return null for invalid numeric strings', () => {
    expect(toNumberOrNull('abc')).toBeNull()
    expect(toNumberOrNull('10abc')).toBeNull()
    expect(toNumberOrNull('abc10')).toBeNull()
  })

  it('should return null for locale formatted strings not parsable by Number', () => {
    expect(toNumberOrNull('1,23')).toBeNull()
  })

  it('should keep NaN if input is the number NaN (current behavior)', () => {
    const result = toNumberOrNull(Number.NaN)
    expect(Number.isNaN(result as number)).toBe(true)
  })
})
