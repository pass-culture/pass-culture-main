import onTimeUpdates from '../onTimeUpdates'

describe('src | components | booking | utils | onTimeUpdates', () => {
  it('return reset object if no or missing arguments', () => {
    const expected = {}
    let args = []
    let result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA']
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', null]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', {}]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
  })
  it('return reset object if invalid arguments', () => {
    const expected = {}
    let args = [null, 'a-name', {}]
    let result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', {}]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', { stockId: 'AAAA' }]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', { bookables: [] }]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', { bookables: null, stockId: 'AAAA' }]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
    args = ['AAAA', 'a-name', { bookables: [], stockId: null }]
    result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
  })
  it('return a valid object with price and stockID', () => {
    const price = 0
    const stockId = 'AAAA'
    const expected = { price, stockId }
    const args = [
      stockId,
      'a-name',
      {
        bookables: [{ id: 'AAAA', price: 0 }],
        stockId: 'AAAA',
      },
    ]
    const result = onTimeUpdates(...args)
    expect(result).toStrictEqual(expected)
  })
})
