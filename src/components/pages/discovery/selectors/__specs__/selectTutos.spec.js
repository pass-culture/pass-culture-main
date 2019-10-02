import selectTutos from '../selectTutos'

describe('src | components | pages | discovery | selectors | selectTutos', () => {
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
      const result = selectTutos(state)

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
