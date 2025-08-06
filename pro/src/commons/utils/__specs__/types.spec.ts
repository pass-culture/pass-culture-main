import { hasProperty, isNumber } from '@/commons/utils/types'

describe('hasProperty', () => {
  it('should return true if the object has the property', () => {
    expect(hasProperty({ someProp: undefined }, 'someProp')).toBe(true)
    expect(hasProperty({ someProp: null }, 'someProp')).toBe(true)
    expect(hasProperty({ someProp: false }, 'someProp')).toBe(true)
    expect(hasProperty({ someProp: 'test' }, 'someProp')).toBe(true)
  })

  it("should return false if the object doesn't have the property", () => {
    expect(hasProperty(undefined, 'someProp')).toBe(false)
    expect(hasProperty(null, 'someProp')).toBe(false)
    expect(hasProperty(false, 'someProp')).toBe(false)
    expect(hasProperty({ someProp: 'test' }, 'otherProp')).toBe(false)
  })
})

describe('isNumber', () => {
  it('should return true is the value is a number and has value', () => {
    expect(isNumber(0)).toBe(true)
    expect(isNumber(1)).toBe(true)
    expect(isNumber(-1)).toBe(true)
    expect(isNumber(1.1)).toBe(true)
    expect(isNumber(-1.1)).toBe(true)
  })
  it('should return false if the value is not a number', () => {
    expect(isNumber(undefined)).toBe(false)
    expect(isNumber(null)).toBe(false)
    expect(isNumber('')).toBe(false)
    expect(isNumber('test')).toBe(false)
    expect(isNumber({})).toBe(false)
    expect(isNumber([])).toBe(false)
    expect(isNumber([1, 2, 3])).toBe(false)
    expect(isNumber({ a: 1 })).toBe(false)
    expect(isNumber({ a: 1, b: 2, c: 3 })).toBe(false)
  })
})
