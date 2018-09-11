import { selectRecommendations } from '../recommendations'
import recommendations from './mocks/putRecommendations'

describe('selectRecommendations', () => {
  it('should return an empty array if there is no recommendations', () => {
    const state = {
      data: {
        recommendations: [{}],
      },
      geolocation: {
        latitude: 'latitude',
        longitude: 'longitude',
      },
    }
    expect(selectRecommendations(state)).toEqual([])
  })

  it('should return selected recommendations', () => {
    const state = {
      data: {
        recommendations,
      },
      geolocation: {
        latitude: 'latitude',
        longitude: 'longitude',
      },
    }

    const expected = {
      dateCreated: '2018-09-06T13:55:26.937798Z',
      dateRead: null,
      dateUpdated: '2018-09-06T13:55:26.937830Z',
      dehumanizedId: 60,
      dehumanizedInviteforEventOccurrenceId: null,
      dehumanizedMediationId: 1,
      dehumanizedOfferId: null,
      dehumanizedUserId: 3,
      distance: '-',
      firstThumbDominantColor: [155, 12, 84],
      id: 'HQ',
      index: 0,
      inviteforEventOccurrenceId: null,
      isClicked: false,
      isFavorite: false,
      isFirst: false,
      mediation: {
        authorId: null,
        backText: null,
        credit: null,
        dateCreated: '2018-09-06T07:57:34.976039Z',
        dateModifiedAtLastProvider: '2018-09-06T07:57:34.976005Z',
        dehumanizedAuthorId: null,
        dehumanizedId: 1,
        dehumanizedLastProviderId: null,
        dehumanizedOfferId: null,
        firstThumbDominantColor: [155, 12, 84],
        frontText: null,
        id: 'AE',
        idAtProviders: null,
        isActive: true,
        lastProviderId: null,
        modelName: 'Mediation',
        offerId: null,
        thumbCount: 1,
        tutoIndex: 0,
      },
      mediationId: 'AE',
      modelName: 'Recommendation',
      offerId: null,
      search: null,
      shareMedium: null,
      thumbUrl: 'http://localhost/storage/thumbs/mediations/AE',
      tz: 'Europe/Paris',
      uniqId: 'tuto_0',
      userId: 'AM',
      validUntilDate: '2018-09-20T13:55:26.908651Z',
    }
    const result = selectRecommendations(state)

    expect(result[0]).toEqual(expected)
  })
})
