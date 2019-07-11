import flattenErrors from '../flattenErrors'

describe('src | components | booking | utils | flattenErrors', () => {
  describe('with array of error', () => {
    it('should return the new array', () => {
      const acc = []
      const err = ['error one', 'error two']
      expect(flattenErrors(acc, err)).toStrictEqual(['error one', 'error two'])
    })
  })

  describe('with one nested level of error', () => {
    it('should return the new array', () => {
      const acc = []
      const err = [['error one', 'error two'], ['error three']]
      expect(flattenErrors(acc, err)).toStrictEqual([
        'error one',
        'error two',
        'error three',
      ])
    })
  })

  describe('with more than one nested level arrays of error', () => {
    it('should return an error', () => {
      const acc = []
      const err = [
        ['error one', 'error two'],
        [['error three'], ['error four']],
      ]
      expect(flattenErrors(acc, err)).not.toEqual([
        'error one',
        'error two',
        'error three',
        'error four',
      ])
    })
  })

  describe('when object of error', () => {
    it('should return the new array', () => {
      const acc = []
      const err = ['error one', { errorTwo: 'error' }]
      expect(flattenErrors(acc, err)).toStrictEqual([
        'error one',
        { errorTwo: 'error' },
      ])
    })
  })
})
