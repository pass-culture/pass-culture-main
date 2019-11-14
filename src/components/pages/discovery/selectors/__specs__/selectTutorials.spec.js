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
              productOrTutoIdentifier: 'tuto_0',
            },
            {
              id: 'BCAD',
              productOrTutoIdentifier: 'tuto_1',
            },
            {
              id: 'NOPE',
              productOrTutoIdentifier: 'product_AB',
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
          productOrTutoIdentifier: 'tuto_0',
        },
        {
          id: 'BCAD',
          productOrTutoIdentifier: 'tuto_1',
        },
      ])
    })
  })
})
