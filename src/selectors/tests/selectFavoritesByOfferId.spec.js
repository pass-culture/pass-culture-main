import selectFavoritesByOfferId from '../selectFavoritesByOfferId'

describe('src | selectors | selectFavoritesByOfferId', () => {
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
    const result = selectFavoritesByOfferId(state, offerId)

    // then
    expect(result).toStrictEqual([])
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
    const thirdFavorite = {
      id: 'CG',
      offerId,
    }
    const state = {
      data: {
        favorites: [firstFavorite, secondFavorite, thirdFavorite],
        offers: [offer],
      },
    }

    // when
    const result = selectFavoritesByOfferId(state, offerId)

    // then
    expect(result).toStrictEqual([secondFavorite, thirdFavorite])
  })
})
