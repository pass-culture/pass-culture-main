import { selectFavoriteById, selectFavoriteByOfferId, selectFavorites } from '../favoritesSelectors'

describe('selectFavorites', () => {
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

describe('src | selectors | selectFavoriteById', () => {
  it('should return undefined when no match', () => {
    // given
    const state = {
      data: {
        favorites: [{ id: 'AE' }],
      },
    }

    // when
    const result = selectFavoriteById('wrong')(state)

    // then
    expect(result).toBeUndefined()
  })

  it('should return favorite matching id', () => {
    // given
    const state = {
      data: {
        favorites: [{ id: 'foo' }, { id: 'bar' }, { id: 'baz' }],
      },
    }

    // when
    const result = selectFavoriteById('bar')(state)

    // then
    expect(result).toStrictEqual({ id: 'bar' })
  })
})

describe('src | selectors | selectFavoriteByOfferId', () => {
  let offer
  let offerId
  beforeEach(() => {
    offerId = 'AE'
    offer = {
      id: offerId,
    }
  })

  it('should return undefined when no match of offerId', () => {
    // given
    const firstFavorite = {
      id: 'AE',
      offerId: 'wrong',
    }
    const secondFavorite = {
      id: 'BF',
      offerId: 'wrong2',
    }
    const thirdFavorite = {
      id: 'CG',
      offerId: 'wrong3',
    }
    const state = {
      data: {
        favorites: [firstFavorite, secondFavorite, thirdFavorite],
        offers: [offer],
      },
    }

    // when
    const result = selectFavoriteByOfferId(state, offerId)

    // then
    expect(result).toBeUndefined()
  })

  it('should return favorites that have offerId', () => {
    // given
    const firstFavorite = {
      id: 'AE',
      offerId: 'wrong',
    }
    const secondFavorite = {
      id: 'BF',
      offerId,
    }
    const state = {
      data: {
        favorites: [firstFavorite, secondFavorite],
        offers: [offer],
      },
    }

    // when
    const result = selectFavoriteByOfferId(state, offerId)

    // then
    expect(result).toStrictEqual(secondFavorite)
  })
})
