import nextRecommendationSelector from '../nextRecommendation'
import state from '../../mocks/reduxState'

describe('nextRecommendationSelector', () => {
  let offerId
  let mediationId

  describe('when the offerId does not exist', () => {
    it('should select the next recommendation corresponding to a mediation', () => {
      // given
      offerId = 'FAKEOFFERID'

      const expected = undefined

      const result = nextRecommendationSelector(state, offerId, mediationId)

      // then
      expect(result).toEqual(expected)
    })
  })

  describe('when there is offerId and no mediationId', () => {
    it('should select the next recommendation corresponding to a mediation', () => {
      // given
      offerId = 'APSA'

      const expected = {
        bookingsIds: [],
        dateCreated: '2018-10-26T05:39:21.816653Z',
        dateRead: null,
        dateUpdated: '2018-10-26T05:39:21.816660Z',
        distance: '10 km',
        firstThumbDominantColor: [5, 31, 49],
        id: 'AFNYU',
        index: 3,
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediation: {
          authorId: 'ALJQ',
          backText: null,
          credit: 'Simon Gosselin',
          dateCreated: '2018-10-11T15:16:52.374071Z',
          dateModifiedAtLastProvider: '2018-10-11T15:16:52.374058Z',
          firstThumbDominantColor: [5, 31, 49],
          frontText: null,
          id: 'ARFA',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Mediation',
          offerId: 'ASKA',
          thumbCount: 1,
          tutoIndex: null,
        },
        mediationId: 'ARFA',
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-10-11T09:33:37.061555Z',
          dateModifiedAtLastProvider: '2018-10-11T09:33:37.061543Z',
          dateRange: ['2018-12-30T18:30:39Z', '2018-12-31T22:30:39Z'],
          productId: 'ARBA',
          product: {
            accessibility: '\u0000',
            ageMax: null,
            ageMin: null,
            conditions: null,
            dateModifiedAtLastProvider: '2018-10-11T09:33:37.057918Z',
            description:
              ' À la frontière du conte oriental contemporain, se tisse une épopée aux accents de Roméo et Juliette judéo-arabe. D’un amour incandescent, entre une étudiante d’origine arabe, Wahida et un jeune juif, Eitan, se greffe, le déchirement de deux familles, deux peuples, deux mémoires, au creux du conflit israélo-palestinien. Aux barrières infranchissables, entre les individus, résonne le télescopage des langues. Exacerbant encore un peu plus les passions, un lourd secret de famille jalonne les épisodes d’une saga où la ferveur se dispute à la figure de l’ennemi.',
            durationMinutes: 240,
            extraData: {
              author: 'Wajdi Mouawad',
              performer: ' Leora Rivlin, Darya Sheizaf, Rafael Tabor ...',
              showSubType: '1304',
              showType: '1300',
              stageDirector: 'Wajdi Mouawad',
            },
            firstThumbDominantColor: null,
            id: 'ARBA',
            idAtProviders: null,
            isNational: false,
            lastProviderId: null,
            mediaUrls: [],
            modelName: 'Event',
            name: 'Tous des oiseaux',
            thumbCount: 0,
            type: 'EventType.SPECTACLE_VIVANT',
          },
          id: 'ASKA',
          idAtProviders: null,
          isActive: true,
          lastProviderId: null,
          modelName: 'Offer',
          stocks: [
            {
              available: 10,
              beginningDatetime: '2018-12-30T18:30:39Z',
              bookingLimitDatetime: '2018-12-28T18:30:39Z',
              bookingRecapSent: null,
              dateModified: '2018-10-11T09:34:21.382659Z',
              dateModifiedAtLastProvider: '2018-10-11T09:34:21.382638Z',
              endDatetime: '2018-12-31T22:30:39Z',
              groupSize: 1,
              id: 'C29A',
              idAtProviders: null,
              isSoftDeleted: false,
              lastProviderId: null,
              modelName: 'Stock',
              offerId: 'ASKA',
              price: 15,
            },
          ],
          venue: {
            address: '15 RUE MALTE BRUN',
            bic: null,
            bookingEmail: 'h.baldini@colline.fr',
            city: 'PARIS 20',
            comment: null,
            dateModifiedAtLastProvider: '2018-10-10T09:01:37.700097Z',
            departementCode: '75',
            firstThumbDominantColor: null,
            iban: null,
            id: 'ASCA',
            idAtProviders: null,
            isVirtual: false,
            lastProviderId: null,
            latitude: 48.86455,
            longitude: 2.39765,
            managingOfferer: {
              address: '15 RUE MALTE BRUN',
              bic: null,
              city: 'PARIS 20',
              dateCreated: '2018-09-05T15:49:18.846677Z',
              dateModifiedAtLastProvider: '2018-09-05T15:49:18.846669Z',
              firstThumbDominantColor: null,
              iban: null,
              id: 'AGVA',
              idAtProviders: null,
              isActive: true,
              lastProviderId: null,
              modelName: 'Offerer',
              name: 'THEATRE NATIONAL DE LA COLLINE',
              postalCode: '75020',
              siren: '784804593',
              thumbCount: 0,
            },
            managingOffererId: 'AGVA',
            modelName: 'Venue',
            name: 'THEATRE NATIONAL DE LA COLLINE',
            postalCode: '75020',
            siret: '78480459300019',
            thumbCount: 0,
          },
          venueId: 'ASCA',
        },
        offerId: 'ASKA',
        path: '/decouverte/ASKA/ARFA',
        search: null,
        shareMedium: null,
        thumbUrl: 'http://localhost/storage/thumbs/mediations/ARFA',
        tz: 'Europe/Paris',
        uniqId: 'product_ARBA',
        userId: 'BU',
        validUntilDate: '2018-10-29T05:39:21.819736Z',
      }

      const result = nextRecommendationSelector(state, offerId, mediationId)

      // then
      expect(result).toEqual(expected)
    })
  })
})
