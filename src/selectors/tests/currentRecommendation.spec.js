import currentRecommendationSelector from '../currentRecommendation'
import state from '../../mocks/reduxState'

describe('currentRecommendationSelector', () => {
  let offerId
  let mediationId

  describe('when there is offerId and no mediationId', () => {
    it('should select the current recommendation corresponding to a mediation', () => {
      // given
      offerId = 'ARBA'

      const expected = {
        bookingsIds: [],
        dateCreated: '2018-10-26T05:39:21.025027Z',
        dateRead: null,
        dateUpdated: '2018-10-26T05:39:21.025036Z',
        distance: '5 km',
        firstThumbDominantColor: [36, 36, 35],
        id: 'AFNYA',
        index: 52,
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediation: {
          authorId: 'AMZQ',
          backText: null,
          credit: 'undefined',
          dateCreated: '2018-10-05T13:16:33.759070Z',
          dateModifiedAtLastProvider: '2018-10-05T13:16:33.759052Z',
          firstThumbDominantColor: [36, 36, 35],
          frontText: null,
          id: 'AP8A',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Mediation',
          offerId: 'ARBA',
          thumbCount: 1,
          tutoIndex: null,
        },
        mediationId: 'AP8A',
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-10-05T13:12:16.482124Z',
          dateModifiedAtLastProvider: '2018-10-05T13:12:16.482118Z',
          dateRange: [],
          product: {
            dateModifiedAtLastProvider: '2018-10-05T13:12:16.478149Z',
            description:
              'Abonnement Premium :  plus de 350 journaux et magazines disponibles en illimité sur tous vos écrans, sans engagement.',
            extraData: null,
            firstThumbDominantColor: null,
            id: 'HE',
            idAtProviders: null,
            isNational: false,
            lastProviderId: null,
            mediaUrls: [],
            modelName: 'Thing',
            name: 'Abonnements presse numérique illimitée',
            thumbCount: 0,
            type: 'ThingType.LIVRE_EDITION',
            url: null,
          },
          id: 'ARBA',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Offer',
          stocks: [
            {
              available: 10000,
              beginningDatetime: null,
              bookingLimitDatetime: null,
              bookingRecapSent: null,
              dateModified: '2018-10-05T13:12:33.318021Z',
              dateModifiedAtLastProvider: '2018-10-05T13:12:33.318016Z',
              endDatetime: null,
              groupSize: 1,
              id: 'CYKA',
              idAtProviders: null,
              isSoftDeleted: false,
              lastProviderId: null,
              modelName: 'Stock',
              offerId: 'ARBA',
              price: 10,
            },
          ],
          productId: 'HE',
          venue: {
            address: '59 Rue Spontini',
            bic: null,
            bookingEmail: 'jflambert@toutabo.com',
            city: 'Paris',
            comment:
              "Merci de contacter l'équipe pass Culture pour lui communiquer le SIRET de ce lieu.",
            dateModifiedAtLastProvider: '2018-10-05T13:10:09.780680Z',
            departementCode: '75',
            firstThumbDominantColor: null,
            iban: null,
            id: 'AQ6Q',
            idAtProviders: null,
            isVirtual: false,
            lastProviderId: null,
            latitude: 48.87001,
            longitude: 2.27846,
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
            name: 'ePresse',
            postalCode: '75116',
            siret: null,
            thumbCount: 0,
          },
          venueId: 'AQ6Q',
        },
        offerId: 'ARBA',
        search: null,
        shareMedium: null,
        thumbUrl: 'http://localhost/storage/thumbs/mediations/AP8A',
        tz: 'Europe/Paris',
        uniqId: 'product_HE',
        userId: 'BU',
        validUntilDate: '2018-10-29T05:39:21.029146Z',
      }

      const result = currentRecommendationSelector(state, offerId, mediationId)

      // then
      expect(result).toEqual(expected)
    })
  })
})
