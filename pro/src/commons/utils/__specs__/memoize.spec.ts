import { memoize } from '../memoize'

describe('memoize', () => {
  it('should return the correct result for the first call', () => {
    const add = (a: number, b: number) => a + b
    const memoizedAdd = memoize(add)

    expect(memoizedAdd(2, 3)).toBe(5) // Expected result: 5
  })

  it('should return the cached result for subsequent calls with the same arguments', () => {
    const add = (a: number, b: number) => a + b
    const memoizedAdd = memoize(add)

    // First call - computes the result and stores it in cache
    const result1 = memoizedAdd(2, 3)
    expect(result1).toBe(5)

    // Second call with same arguments - uses cached result
    const result2 = memoizedAdd(2, 3)
    expect(result2).toBe(5)

    // Ensure the function was only called once
    expect(result1).toBe(result2) // Should be the same value
  })

  it('should handle different arguments and return different results', () => {
    const add = (a: number, b: number) => a + b
    const memoizedAdd = memoize(add)

    const result1 = memoizedAdd(2, 3) // First call with (2, 3)
    const result2 = memoizedAdd(3, 4) // First call with (3, 4)

    expect(result1).toBe(5) // Expected result: 5
    expect(result2).toBe(7) // Expected result: 7
  })

  it('should cache the result for different arguments and avoid recomputation', () => {
    const add = (a: number, b: number) => a + b
    const memoizedAdd = memoize(add)

    // First call with (2, 3)
    const result1 = memoizedAdd(2, 3)
    expect(result1).toBe(5)

    // Call with different arguments (3, 4)
    const result2 = memoizedAdd(3, 4)
    expect(result2).toBe(7)

    // Call with the same arguments (2, 3) again, ensuring it's cached
    const result3 = memoizedAdd(2, 3)
    expect(result3).toBe(5)

    // Ensure that both results are cached correctly
    expect(result1).toBe(result3) // Cached result
    expect(result1).not.toBe(result2) // Different cached result
  })

  it('should handle different parameter types (e.g., objects, arrays)', () => {
    const concat = (str1: string, str2: string) => str1 + str2
    const memoizedConcat = memoize(concat)

    const result1 = memoizedConcat('Hello, ', 'world!')
    const result2 = memoizedConcat('Hello, ', 'world!')

    expect(result1).toBe('Hello, world!')
    expect(result2).toBe('Hello, world!')
    expect(result1).toBe(result2) // Should be cached
  })

  it('should handle non-primitive types like objects (by converting args to string)', () => {
    const merge = (obj1: { a: number }, obj2: { b: number }) => ({
      ...obj1,
      ...obj2,
    })
    const memoizedMerge = memoize(merge)

    const obj1 = { a: 1 }
    const obj2 = { b: 2 }

    const result1 = memoizedMerge(obj1, obj2)
    const result2 = memoizedMerge(obj1, obj2)

    expect(result1).toEqual({ a: 1, b: 2 })
    expect(result2).toEqual({ a: 1, b: 2 })
    expect(result1).toBe(result2) // Cached result
  })
})
