const { expect } = require('chai')
const helper = require('./getPrice')

describe('getPrice - format a value with devise', () => {
  describe('is not defined', () => {
    it('should return an empty string if value is evaluated to undefined|null', () => {
      // <!-- legacy
      const expected = ''
      let value
      let result = helper.getPrice(value)
      expect(result).to.equal(expected)
      // --> }
      value = null
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
      value = 'null'
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
      value = new Error(null)
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
    })
  })
  describe('is empty', () => {
    it('should return a default string if is equal to 0', () => {
      // <!-- legacy
      let value = 0
      let expected = helper.defaultFreeValue
      let result = helper.getPrice(value)
      expect(result).to.equal(expected)
      // with default 'free' argument value
      expected = 'toto'
      result = helper.getPrice(value, 'toto')
      expect(result).to.equal(expected)
      // --> }
      value = false
      expected = helper.defaultFreeValue
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
      value = true
      expected = helper.defaultFreeValue
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
      value = {}
      expected = helper.defaultFreeValue
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
      value = []
      expected = helper.defaultFreeValue
      result = helper.getPrice(value)
      expect(result).to.equal(expected)
    })
  })
  it('should return value with devise', () => {
    // <!-- legacy
    let value = 12
    let expected = '12€'
    let result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = '12'
    expected = '12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = 12.42
    expected = '12,42€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = '12.42'
    expected = '12,42€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    // --> }
    value = '1222.00'
    expected = '1222,00€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = '0.00'
    expected = '0,00€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = '0'
    expected = '0€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
  })
})
