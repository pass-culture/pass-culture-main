// $(yarn bin)/jest --env=jsdom ./src/selectors/tests/searchSelectors.spec.js --watch
import { selectCurrentSearchRecommendation } from '../searchSelectors'

describe('src | selectors | searchSelectors', () => {
  it('return null when mediationId and offerId are not defined', () => {
    // given
    const state = {
      data: {
        searchRecommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = undefined
    const mediationId = undefined
    const result = selectCurrentSearchRecommendation(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result).toStrictEqual(null)
  })

  it('return null when any recommantions is matching with offerId or mediationId', () => {
    // given
    const state = {
      data: {
        searchRecommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'ZZZZ'
    const mediationId = '0000'
    const result = selectCurrentSearchRecommendation(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result).toStrictEqual(null)
  })

  it('return null when recommendations are empties', () => {
    // given
    const state = {
      data: {
        searchRecommendations: [],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '1234'
    const result = selectCurrentSearchRecommendation(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result).toStrictEqual(null)
  })

  it('return recommendation with offerId AAAA when mediationId 5678', () => {
    // given
    const state = {
      data: {
        searchRecommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '5678'
    const result = selectCurrentSearchRecommendation(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })

  it('return recommendation with offerId BBBB when mediationId is 5678', () => {
    // given
    const state = {
      data: {
        searchRecommendations: [
          { mediationId: '1234', offerId: 'AAAA' },
          { mediationId: '5678', offerId: 'BBBB' },
        ],
      },
    }

    // when
    const offerId = 'AAAA'
    const mediationId = '5678'
    const result = selectCurrentSearchRecommendation(
      state,
      offerId,
      mediationId
    )

    // then
    expect(result.mediationId).toStrictEqual('1234')
  })
})
