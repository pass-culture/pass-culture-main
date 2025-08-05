import { isEqual } from '../isEqual'

describe('isEqual', () => {
  it('should return true for two identical primitive values', () => {
    expect(isEqual(5, 5)).toBe(true)
    expect(isEqual('hello', 'hello')).toBe(true)
    expect(isEqual(true, true)).toBe(true)
  })

  it('should return false for different primitive values', () => {
    expect(isEqual(5, 10)).toBe(false)
    expect(isEqual('hello', 'world')).toBe(false)
    expect(isEqual(true, false)).toBe(false)
  })

  it('should return true for two identical objects with same keys and values', () => {
    const obj1 = { a: 1, b: 2 }
    const obj2 = { a: 1, b: 2 }
    expect(isEqual(obj1, obj2)).toBe(true)
  })

  it('should return false for objects with different keys', () => {
    const obj1 = { a: 1, b: 2 }
    const obj2 = { a: 1, c: 3 }
    expect(isEqual(obj1, obj2)).toBe(false)
  })

  it('should return false for objects with different values for the same key', () => {
    const obj1 = { a: 1, b: 2 }
    const obj2 = { a: 1, b: 3 }
    expect(isEqual(obj1, obj2)).toBe(false)
  })

  it('should return true for two identical arrays', () => {
    const arr1 = [1, 2, 3]
    const arr2 = [1, 2, 3]
    expect(isEqual(arr1, arr2)).toBe(true)
  })

  it('should return false for arrays with different lengths', () => {
    const arr1 = [1, 2, 3]
    const arr2 = [1, 2]
    expect(isEqual(arr1, arr2)).toBe(false)
  })

  it('should return false for arrays with different elements', () => {
    const arr1 = [1, 2, 3]
    const arr2 = [1, 3, 2]
    expect(isEqual(arr1, arr2)).toBe(false)
  })

  it('should return true for identical nested objects', () => {
    const obj1 = { a: 1, b: { c: 2, d: 3 } }
    const obj2 = { a: 1, b: { c: 2, d: 3 } }
    expect(isEqual(obj1, obj2)).toBe(true)
  })

  it('should return false for objects with nested objects having different values', () => {
    const obj1 = { a: 1, b: { c: 2, d: 3 } }
    const obj2 = { a: 1, b: { c: 2, d: 4 } }
    expect(isEqual(obj1, obj2)).toBe(false)
  })

  it('should return true for null and undefined being equal to null and undefined respectively', () => {
    expect(isEqual(null, null)).toBe(true)
    expect(isEqual(undefined, undefined)).toBe(true)
  })

  it('should return false for null and undefined being compared to non-null/non-undefined values', () => {
    expect(isEqual(null, undefined)).toBe(false)
    expect(isEqual(undefined, null)).toBe(false)
  })
})
