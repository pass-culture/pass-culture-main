import { describe, expect, it } from 'vitest'

import { nullifyEmptyProps } from '../nullifyEmptyProps'

describe('nullifyEmptyProps', () => {
  it('should convert empty strings to null', () => {
    const input = { a: '', b: '   ' }

    const result = nullifyEmptyProps(input)

    expect(result).toEqual({ a: null, b: null })
  })

  it('should convert empty arrays to null', () => {
    const input = { a: [], b: [1], c: ['x'] }

    const result = nullifyEmptyProps(input)

    expect(result).toEqual({ a: null, b: [1], c: ['x'] })
  })

  it('should leave non-empty strings unchanged', () => {
    const input = { name: 'john', city: 'Paris' }

    const result = nullifyEmptyProps(input)

    expect(result).toEqual({ name: 'john', city: 'Paris' })
  })

  it('should leave non-string, non-array values unchanged', () => {
    const input = {
      n: 0,
      f: false,
      t: true,
      o: { k: '' },
      d: new Date(0),
      u: undefined,
      nil: null,
    }

    const result = nullifyEmptyProps(input)

    // Only top-level empty string/array are nullified; nested values remain as-is
    expect(result).toEqual({
      n: 0,
      f: false,
      t: true,
      o: { k: '' },
      d: new Date(0),
      u: undefined,
      nil: null,
    })
  })

  it('should not mutate the original object, even with nested objects', () => {
    const input = { a: 'abc', b: [1, 2, 3], c: 'x', nested: { d: 'def' } }

    const result = nullifyEmptyProps(input)

    expect(result).toEqual(input)
    expect(result).not.toBe(input)
    expect(result.nested).not.toBe(input.nested)
  })
})
