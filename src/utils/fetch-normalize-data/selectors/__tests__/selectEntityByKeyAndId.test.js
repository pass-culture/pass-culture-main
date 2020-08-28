import selectEntityByKeyAndId from '../selectEntityByKeyAndId'

describe('selectEntityByKeyAndId', () => {
  describe('when datum is not here', () => {
    it('should return undefined', () => {
      // given
      const state = {
        data: {
          foos: [],
        },
      }

      // when
      const result = selectEntityByKeyAndId(state, 'foos', 'AE')

      // then
      expect(result).toBeUndefined()
    })
  })

  describe('when datum is here', () => {
    it('should return the datum', () => {
      // given
      const selectedFoo = {
        id: 'AE',
      }
      const state = {
        data: {
          foos: [
            selectedFoo,
            {
              id: 'BF',
            },
          ],
        },
      }

      // when
      const result = selectEntityByKeyAndId(state, 'foos', 'AE')

      // then
      expect(result).toStrictEqual(selectedFoo)
    })
  })
})
