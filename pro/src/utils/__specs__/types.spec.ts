import { hasProperty } from 'utils/types'

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
