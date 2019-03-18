import selectRecommendation from '../recommendation'
import state from '../../mocks/reduxState'

describe('selectRecommendation', () => {
  describe('when the recommendationId exists', () => {
    it('should select the corresponding recommendation', () => {
      // given
      const recommendationId = 'AFNVK'
      const expected = {
        bookingsIds: [],
        dateCreated: '2018-10-25T19:48:46.812732Z',
        dateRead: null,
        dateUpdated: '2018-10-25T19:48:46.812742Z',
        id: 'AFNVK',
        isClicked: true,
        isFavorite: false,
        isFirst: false,
        mediation: {
          authorId: 'AMZQ',
          backText: null,
          credit: 'Toutabo',
          dateCreated: '2018-09-14T14:04:00.180857Z',
          dateModifiedAtLastProvider: '2018-09-14T14:04:00.180850Z',
          firstThumbDominantColor: [245, 243, 237],
          frontText: null,
          id: 'ALGA',
          idAtProviders: null,
          isActive: false,
          lastProviderId: null,
          modelName: 'Mediation',
          offerId: 'AM3A',
          thumbCount: 1,
          tutoIndex: null,
        },
        mediationId: 'ALGA',
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-09-14T13:46:33.401791Z',
          dateModifiedAtLastProvider: '2018-09-14T13:46:33.401781Z',
          dateRange: [],
          eventId: null,
          eventOrThing: {
            dateModifiedAtLastProvider: '2018-09-14T13:46:33.399386Z',
            description:
              'Abonnement Premium :  plus de 350 journaux et magazines disponibles en illimité sur tous vos écrans, sans engagement.',
            extraData: null,
            firstThumbDominantColor: null,
            id: 'CM',
            idAtProviders: null,
            isNational: false,
            lastProviderId: null,
            mediaUrls: [],
            modelName: 'Thing',
            name: 'Abonnement presse numérique illimitée',
            thumbCount: 0,
            type: 'ThingType.PRESSE_ABO',
            url: 'www.epresse.fr',
          },
          id: 'AM3A',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Offer',
          stocks: [
            {
              available: 5000,
              beginningDatetime: null,
              bookingLimitDatetime: null,
              bookingRecapSent: null,
              dateModified: '2018-09-14T14:04:39.745053Z',
              dateModifiedAtLastProvider: '2018-09-14T14:04:39.745046Z',
              endDatetime: null,
              groupSize: 1,
              id: 'CPGQ',
              idAtProviders: null,
              isSoftDeleted: false,
              lastProviderId: null,
              modelName: 'Stock',
              offerId: 'AM3A',
              price: 10,
            },
          ],
          thingId: 'CM',
          venue: {
            address: null,
            bic: null,
            bookingEmail: null,
            city: null,
            comment: null,
            dateModifiedAtLastProvider: '2018-09-12T14:58:23.792014Z',
            departementCode: null,
            firstThumbDominantColor: null,
            iban: null,
            id: 'AMVQ',
            idAtProviders: null,
            isVirtual: true,
            lastProviderId: null,
            latitude: null,
            longitude: null,
            managingOfferer: {
              address: '59 RUE SPONTINI',
              bic: null,
              city: 'PARIS 16',
              dateCreated: '2018-09-12T14:58:23.782625Z',
              dateModifiedAtLastProvider: '2018-09-12T14:58:23.782618Z',
              firstThumbDominantColor: null,
              iban: null,
              id: 'A9QA',
              idAtProviders: null,
              isActive: true,
              lastProviderId: null,
              modelName: 'Offerer',
              name: 'TOUTABO',
              postalCode: '75116',
              siren: '480467000',
              thumbCount: 0,
            },
            managingOffererId: 'A9QA',
            modelName: 'Venue',
            name: 'Offre en ligne',
            postalCode: null,
            siret: null,
            thumbCount: 0,
          },
          venueId: 'AMVQ',
        },
        offerId: 'AM3A',
        search: null,
        shareMedium: null,
        userId: 'V9',
        validUntilDate: '2018-10-28T19:48:46.809836Z',
      }

      // when
      const result = selectRecommendation(state, recommendationId)
      expect(result).toEqual(expected)
    })
  })

  describe('when the recommendationId does not exist', () => {
    it.skip('should return empty string', () => {
      // given
      const recommendationId = null
      const expected = ''

      // when
      const result = selectRecommendation(state, recommendationId)
      expect(result).toEqual(expected)
    })
  })
})
