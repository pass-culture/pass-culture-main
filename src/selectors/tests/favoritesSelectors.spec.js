import { selectFavorites } from '../favoritesSelectors'

describe('src | selectors | favoritesSelectors', () => {
  it('should return favorites data from state', () => {
    // given
    const state = {
      data: {
        favorites: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const result = selectFavorites(state)

    // then
    expect(result).toStrictEqual([
      { mediationId: '1234', offerId: 'AAAA' },
      { mediationId: '5678', offerId: 'BBBB' },
    ])
  })
})
