import { isPlainObject } from '../isPlainObject'

describe('isPlainObject', () => {
  it('should works with only plain objects', () => {
    expect(isPlainObject({})).toBe(true)
    expect(isPlainObject({ a: { b: 1 } })).toBe(true)
    expect(isPlainObject({ a: { b: () => {} } })).toBe(true)
    expect(isPlainObject(Object.create(null))).toBe(true)
    expect(isPlainObject(new Object())).toBe(true)

    expect(isPlainObject(new Date())).toBe(false)
    expect(isPlainObject([])).toBe(false)
    expect(isPlainObject(() => {})).toBe(false)

    expect(isPlainObject(class TestClass {})).toBe(false)
  })
})
