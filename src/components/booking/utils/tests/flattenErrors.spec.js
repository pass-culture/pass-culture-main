// jest ./src/components/booking/utils/tests/flattenErrors --watch
import flattenErrors from '../flattenErrors'

describe('src | components | booking | utils', () => {
  describe('flattenErrors', () => {
    describe('when array of error', () => {
      it('should return the new array', () => {
        const acc = ['error one']
        const err = ['error two']
        expect(flattenErrors(acc, err)).toEqual(['error one', 'error two'])
      })
    })

    describe('when object of error', () => {
      it('should return the new array', () => {
        const acc = ['error one']
        const err = { errorTwo: 'error' }
        expect(flattenErrors(acc, err)).toEqual([
          'error one',
          { errorTwo: 'error' },
        ])
      })
    })
  })
})
