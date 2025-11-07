import { describe, expect, it } from 'vitest'

import { toEnumOrNull } from '../toEnumOrNull'

enum ColorEnum {
  RED = 'RED',
  GREEN = 'GREEN',
  BLUE = 'BLUE',
}

enum NumberEnum {
  ONE = 1,
  TWO = 2,
  THREE = 3,
}

describe('toEnumOrNull', () => {
  it('should return the value when it exists in a string enum', () => {
    expect(toEnumOrNull('RED', ColorEnum)).toBe('RED')
    expect(toEnumOrNull('GREEN', ColorEnum)).toBe('GREEN')
  })

  it('should return null when value not in string enum', () => {
    expect(toEnumOrNull('PURPLE', ColorEnum)).toBeNull()
    expect(toEnumOrNull('', ColorEnum)).toBeNull()
  })

  it('should return the value when it exists in a number enum-like object', () => {
    expect(toEnumOrNull(1, NumberEnum)).toBe(1)
    expect(toEnumOrNull(3, NumberEnum)).toBe(3)
  })

  it('should return null when number not present', () => {
    expect(toEnumOrNull(4, NumberEnum)).toBeNull()
    expect(toEnumOrNull(-1, NumberEnum)).toBeNull()
  })

  it('should handle mixed type mismatches returning null', () => {
    expect(toEnumOrNull('1', NumberEnum)).toBeNull()
    expect(toEnumOrNull(1, ColorEnum)).toBeNull()
  })

  it('should return null for undefined / null inputs', () => {
    expect(toEnumOrNull(undefined, ColorEnum)).toBeNull()
    expect(toEnumOrNull(null, ColorEnum)).toBeNull()
  })

  it('should work with an enum object having numeric string members (edge)', () => {
    const MixedEnum = { A: '1', B: '2' } as const
    expect(toEnumOrNull('1', MixedEnum)).toBe('1')
    expect(toEnumOrNull(1, MixedEnum)).toBeNull()
  })

  it('should not mutate the enum object', () => {
    const snapshot = { ...ColorEnum }
    toEnumOrNull('RED', ColorEnum)
    expect(ColorEnum).toEqual(snapshot)
  })
})
