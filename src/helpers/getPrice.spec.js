const { expect } = require('chai')
const helper = require('./getPrice')

describe('getPrice - format a value with devise', () => {
  it('should return empty string if undefined || null', () => {
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
  it('should return a empty string if === 0 || invalid', () => {
    const expected = ''
    let value = false
    let result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = true
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = {}
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = []
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [null, undefined]
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [true, {}]
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
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
    // // --> }
    value = '1222.00'
    expected = '1222€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
  })
  it('should return 0€', () => {
    const expected = '0€'
    let value = '0.00'
    let result = helper.getPrice(value)
    expect(result).to.equal(expected)
    expect(result).to.equal(expected)
    value = 0
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = '0'
    result = helper.getPrice(value)
    value = [0, undefined]
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [0, []]
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [0, {}]
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
  })
  it('should return value with devise from array', () => {
    // <!-- legacy
    let value = [6, 12]
    let expected = '6€ - 12€'
    let result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['6', '12']
    expected = '6€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['6', '3', '49', '12']
    expected = '3€ - 49€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [12, 6]
    expected = '6€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [12, 0]
    expected = '0€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = [0, 12]
    expected = '0€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['0', '12']
    expected = '0€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['12', '0']
    expected = '0€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['12', '0.00']
    expected = '0€ - 12€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
    value = ['349', '12', '49', null, '28', '0.00', '3']
    expected = '0€ - 349€'
    result = helper.getPrice(value)
    expect(result).to.equal(expected)
  })
})
