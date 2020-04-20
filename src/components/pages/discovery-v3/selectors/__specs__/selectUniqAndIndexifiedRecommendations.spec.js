import selectUniqAndIndexifiedRecommendations from '../selectUniqAndIndexifiedRecommendations'

describe('src | components | pages | discovery | selectors | selectUniqAndIndexifiedRecommendations', () => {
  it('should return an empty array if there are no recommendations', () => {
    // given
    const state = {
      data: {
        recommendations: [],
      },
      geolocation: {
        latitude: 48.8637,
        longitude: 2.3374,
        watchId: 1,
      },
    }

    // when
    const result = selectUniqAndIndexifiedRecommendations(state)

    // then
    expect(result).toStrictEqual([])
  })

  it('should return recommendations', () => {
    // given
    const recommendation = {
      bookingsIds: [],
      dateCreated: '2018-10-10T14:19:27.410551Z',
      dateRead: null,
      dateUpdated: '2018-10-10T14:19:27.410609Z',
      distance: '5444 km',
      id: 'AEWPS',
      index: 0,
      isClicked: true,
      isFavorite: false,
      isFirst: false,
      mediationId: 'AKSA',
      modelName: 'Recommendation',
      offerId: 'AKLA',
      search: 'page=1',
      shareMedium: null,
      thumbUrl: 'http://localhost/storage/thumbs/mediations/AKSA',
      uniqId: 'product_BE',
      userId: 'AQBA',
    }
    const state = {
      data: {
        recommendations: [recommendation],
      },
    }

    // when
    const result = selectUniqAndIndexifiedRecommendations(state)

    // then
    expect(result[0]).toStrictEqual(recommendation)
    expect(result).toHaveLength(1)
  })
})
