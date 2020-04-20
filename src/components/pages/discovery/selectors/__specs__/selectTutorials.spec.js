import selectTutorials from '../selectTutorials'

describe('src | components | pages | discovery | selectors | selectTutorials', () => {
  describe('when there are tutos in recommendation', () => {
    it('should select the tutos', () => {
      // given
      const state = {
        data: {
          recommendations: [
            {
              id: 'ABCD',
              productIdentifier: 'tuto_0',
            },
            {
              id: 'BCAD',
              productIdentifier: 'tuto_1',
            },
            {
              id: 'NOPE',
              productIdentifier: 'product_AB',
            },
          ],
        },
      }

      // when
      const result = selectTutorials(state)

      // then
      expect(result).toStrictEqual([
        {
          id: 'ABCD',
          productIdentifier: 'tuto_0',
        },
        {
          id: 'BCAD',
          productIdentifier: 'tuto_1',
        },
      ])
    })
  })
})
