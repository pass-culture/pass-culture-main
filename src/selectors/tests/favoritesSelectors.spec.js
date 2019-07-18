import { selectMyFavorites } from '../favoritesSelectors'

describe('src | selectors | searchSelectors', () => {
  it('return null when mediationId and offerId are not defined', () => {
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
    const offerId = undefined
    const mediationId = undefined
    const result = selectMyFavorites(state, offerId, mediationId)

    // then
    expect(result).toStrictEqual([])
  })

  it('return null when any recommantions is matching with offerId or mediationId', () => {
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
    const offerId = 'ZZZZ'
    const mediationId = '0000'
    const result = selectMyFavorites(state, offerId, mediationId)

    // then
    expect(result).toStrictEqual([])
  })

  it('return null when recommendations are empties', () => {
    // given
    const state = {
      data: {
        favorites: [],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '1234'
    const result = selectMyFavorites(state, offerId, mediationId)

    // then
    expect(result).toStrictEqual([])
  })

  it('return favorite with offerId AAAA when mediationId 5678', () => {
    // given
    const state = {
      data: {
        favorites: [
          {
            mediationId: '1234',
            offer: {
              id: 'AAAA'
            },
            offerId: 'AAAA',
            mediation: {
              id: '1234'
            }
          },
          {
            mediationId: '5678',
            offer: {
              id: 'BBBB'
            },
            offerId: 'BBBB',
            mediation: {
              id: '5678'
            }
          },
        ],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '1234'
    const result = selectMyFavorites(state, offerId, mediationId)

    // then
    expect(result.offerId).toStrictEqual('AAAA')
  })

  it('return recommendation with offerId BBBB when mediationId is 5678', () => {
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
    const offerId = 'AAAA'
    const mediationId = '5678'
    const result = selectMyFavorites(state, offerId, mediationId)

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })
})
