import { shallow } from 'enzyme'
import React from 'react'
import Dotdotdot from 'react-dotdotdot'

import state from '../../../../mocks/global_state_1'
import { SearchResultItem } from '../SearchResultItem'
import { selectRecommendations } from '../../../../selectors'

describe('src | components | pages | search | SearchResultItem', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      dispatch: fakeMethod,
      history: {
        push: fakeMethod,
      },
      location: {
        pathname: '/recherche/resultats',
        search: '?categories=Applaudir',
      },
      recommendation: {
        bookingsIds: [],
        dateCreated: '2018-09-10T08:04:49.264895Z',
        dateRead: null,
        dateUpdated: '2018-09-10T08:04:49.264905Z',
        dehumanizedId: 128,
        dehumanizedMediationId: null,
        dehumanizedOfferId: 186,
        dehumanizedUserId: 1,
        id: 'QA',
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediationId: null,
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-09-06T08:17:50.169269Z',
          dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
          dateRange: [],
          dehumanizedEventId: null,
          dehumanizedId: 186,
          dehumanizedLastProviderId: 6,
          dehumanizedThingId: 129,
          dehumanizedVenueId: 2,
          id: 'X9',
          idAtProviders: '2921:9782367740911',
          lastProviderId: 'AY',
          modelName: 'Offer',
          name: 'sur la route des migrants ; rencontres à Calais',
          product: {
            dateModifiedAtLastProvider: '2018-01-30T00:00:00Z',
            dehumanizedId: 129,
            dehumanizedLastProviderId: 8,
            description: null,
            extraData: {
              author: 'Jouve, Jessica ;Dufour, Anthony',
              dewey: '840',
              num_in_collection: '0',
              prix_livre: '12.90',
              rayon: 'Littérature française',
              titelive_regroup: '0',
            },
            firstThumbDominantColor: [12, 62, 123],
            id: 'QE',
            idAtProviders: '9782367740911',
            isActive: false,
            lastProviderId: 'BA',
            mediaUrls: [],
            modelName: 'Product',
            offerType: {
              appLabel: 'Livres, cartes bibliothèque ou médiathèque',
              conditionalFields: [],
              description: "S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?",
              offlineOnly: false,
              onlineOnly: true,
              proLabel: "Presse  Abonnements",
              sublabel: "Lire",
              type: "Thing",
              value: "ThingType.PRESSE_ABO",
            },
            thumbCount: 2,
            type: 'Book',
            url: null,
          },
          productId: 'QE',
          venue: {
            address: '72 rue Carnot',
            bookingEmail: 'passculture-dev@beta.gouv.fr',
            city: 'ROMAINVILLE',
            dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
            dehumanizedId: 2,
            dehumanizedLastProviderId: 7,
            dehumanizedManagingOffererId: 2,
            departementCode: '93',
            firstThumbDominantColor: null,
            id: 'A9',
            idAtProviders: '2921',
            isVirtual: false,
            lastProviderId: 'A4',
            latitude: 2.44072,
            longitude: 48.88381,
            managingOfferer: {
              address: '72 rue Carnot',
              city: 'ROMAINVILLE',
              dateCreated: '2018-09-06T08:16:23.133432Z',
              dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
              dehumanizedId: 2,
              dehumanizedLastProviderId: 7,
              firstThumbDominantColor: null,
              id: 'A9',
              idAtProviders: '2921',
              isActive: true,
              lastProviderId: 'A4',
              modelName: 'Offerer',
              name: 'Les Pipelettes',
              postalCode: '93230',
              siren: '302559639',
              thumbCount: 0,
            },
            managingOffererId: 'A9',
            modelName: 'Venue',
            name: 'Les Pipelettes',
            postalCode: '93230',
            siret: '30255963934017',
            thumbCount: 0,
          },
          venueId: 'A9',
        },
        offerId: 'X9',
        search: null,
        shareMedium: null,
        thumbUrl: 'http://localhost/storage/thumbs/products/QE',
        userId: 'AE',
        validUntilDate: '2018-09-11T08:04:49.273248Z',
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    // [props.recommendation] = selectRecommendations(state)

    // when
    const wrapper = shallow(<SearchResultItem {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('onSuccessLoadRecommendationDetails()', () => {
    it('should push URL in history', () => {
      // given
      const linkURL = `${props.location.pathname}/item/${props.recommendation.offerId}${props.location.search}`

      // when
      const wrapper = shallow(<SearchResultItem {...props} />)
      wrapper.instance().onSuccessLoadRecommendationDetails()

      // then
      expect(props.history.push).toHaveBeenCalledWith(linkURL)
      props.history.push.mockClear()
    })
  })

  describe('markSearchRecommendationsAsClicked()', () => {
    it('should dispatch the request data', () => {
      // when
      const wrapper = shallow(<SearchResultItem {...props} />)
      wrapper.instance().markSearchRecommendationsAsClicked()

      // then
      expect(props.dispatch).toHaveBeenCalled()
      props.dispatch.mockClear()
    })
  })

  describe('render()', () => {
    it('should have one item result details', () => {
      // when
      const wrapper = shallow(<SearchResultItem {...props} />)
      const img = wrapper.find('img').props()
      const h5 = wrapper.find('h5').props()
      const dotdotdot = wrapper.find(Dotdotdot).props()
      const recommendationDate = wrapper.find('.fs13').last().text()
      const first = wrapper.find('.fs13').first().text()

      // then
      expect(img.src).toBe('http://localhost/storage/thumbs/products/QE')
      expect(h5.title).toBe(
        'sur la route des migrants ; rencontres à Calais'
      )
      expect(dotdotdot.children).toBe(
        'sur la route des migrants ; rencontres à Calais'
      )
      expect(first).toBe('Livres, cartes bibliothèque ou médiathèque')
      expect(recommendationDate).toBe('permanent')
    })
  })
})
