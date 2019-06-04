import { shallow } from 'enzyme'
import React from 'react'

import { SearchResults } from '../SearchResults'
import { SearchResultItemContainer as SearchResultItem } from '../SearchResultItem'

describe('src | components | pages | search | SearchResults', () => {
  const fakeMethod = jest.fn()
  let props

  beforeEach(() => {
    props = {
      cameFromOfferTypesPage: true,
      hasMore: false,
      items: [],
      keywords: 'fakeKeywords',
      query: {
        add: fakeMethod,
        change: fakeMethod,
        clear: fakeMethod,
        parse: () => ({ page: '1' }),
        remove: fakeMethod,
      },
    }
  })

  it('should match the snapshot', () => {
    // given
    props.cameFromOfferTypesPage = false

    // when
    const wrapper = shallow(<SearchResults {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  describe('handleSetHasReceivedFirstSuccessData()', () => {
    it('should return hasReceivedFirstSuccessData = true if there are data', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ hasReceivedFirstSuccessData: false })
      wrapper.instance().handleSetHasReceivedFirstSuccessData()

      // then
      expect(wrapper.state(['hasReceivedFirstSuccessData'])).toBe(true)
    })

    it('should return undefined if there are no data', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ hasReceivedFirstSuccessData: true })
      const handleSetHasReceivedFirstSuccessData = wrapper
        .instance()
        .handleSetHasReceivedFirstSuccessData()

      // then
      expect(handleSetHasReceivedFirstSuccessData).toBeUndefined()
    })
  })

  describe('handleShouldCancelLoading()', () => {
    it('should return isLoading = false if its loading', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ isLoading: true })
      wrapper.instance().handleShouldCancelLoading()

      // then
      expect(wrapper.state(['isLoading'])).toBe(false)
    })

    it('should return undefined if its not loading', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      const handleShouldCancelLoading = wrapper
        .instance()
        .handleShouldCancelLoading()

      // then
      expect(handleShouldCancelLoading).toBeUndefined()
    })
  })

  describe('loadMore()', () => {
    const page = 10

    it('should return undefined if its loading', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.setState({ isLoading: true })
      const loadMore = wrapper.instance().loadMore(page)

      // then
      expect(loadMore).toBeUndefined()
    })

    it('should called query change if its not loading', () => {
      // when
      const wrapper = shallow(<SearchResults {...props} />)
      wrapper.instance().loadMore(page)

      // then
      expect(wrapper.state(['isLoading'])).toBe(true)
      expect(props.query.change).toBeCalledWith(
        { page },
        { historyMethod: 'replace' }
      )
      props.query.change.mockClear()
    })
  })

  describe('render()', () => {
    const items = [
      {
        bookings: [],
        dateCreated: '2018-09-21T10:06:06.832247Z',
        dateRead: null,
        dateUpdated: '2018-09-21T10:06:06.832255Z',
        dehumanizedId: 67,
        dehumanizedMediationId: null,
        dehumanizedOfferId: 135,
        dehumanizedUserId: 1,
        id: '9M',
        isClicked: false,
        isFavorite: false,
        isFirst: false,
        mediationId: null,
        modelName: 'Recommendation',
        offer: {
          bookingEmail: null,
          dateCreated: '2018-09-21T09:16:38.510799Z',
          dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
          dateRange: [],
          dehumanizedEventId: null,
          dehumanizedId: 135,
          dehumanizedLastProviderId: 6,
          dehumanizedThingId: 333,
          dehumanizedVenueId: 1,
          id: 'Q4',
          idAtProviders: '2949:9782221190081',
          lastProviderId: 'AY',
          modelName: 'Offer',
          product: {
            dateModifiedAtLastProvider: '2018-01-31T00:00:00Z',
            dehumanizedId: 333,
            dehumanizedLastProviderId: 8,
            description: null,
            extraData: {
              author: 'Hall, Maggie',
              dewey: '800',
              num_in_collection: '0',
              prix_livre: '17.90',
              rayon: 'Litt\u00e9rature jeunesse Romans / Contes / Fables',
              titelive_regroup: '0',
            },
            firstThumbDominantColor: [45, 34, 70],
            id: 'AFGQ',
            idAtProviders: '9782221190081',
            isActive: true,
            isNational: false,
            lastProviderId: 'BA',
            mediaUrls: [],
            modelName: 'Product',
            name: 'la conspiration T.3 ; les confins du monde',
            thumbCount: 2,
            type: 'LIVRE_EDITION',
            url: null,
          },
          productId: 'AFGQ',
          stocks: [
            {
              available: null,
              beginningDatetime: null,
              bookingLimitDatetime: null,
              bookingRecapSent: null,
              dateModified: '2018-09-21T09:16:38.552923Z',
              dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
              dehumanizedId: 135,
              dehumanizedLastProviderId: 6,
              dehumanizedOfferId: 135,
              endDatetime: null,
              groupSize: 1,
              id: 'Q4',
              idAtProviders: '2949:9782221190081',
              isSoftDeleted: false,
              lastProviderId: 'AY',
              modelName: 'Stock',
              offerId: 'Q4',
              price: 17.9,
            },
          ],
          venue: {
            address: '41 Boulevard de Strasbourg',
            bookingEmail: 'passculture-dev@beta.gouv.fr',
            city: 'AULNAY SOUS BOIS',
            dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
            dehumanizedId: 1,
            dehumanizedLastProviderId: 7,
            dehumanizedManagingOffererId: 1,
            departementCode: '93',
            firstThumbDominantColor: null,
            id: 'AE',
            idAtProviders: '2949',
            isVirtual: false,
            lastProviderId: 'A4',
            latitude: 2.49114,
            longitude: 48.92799,
            managingOfferer: {
              address: '41 Boulevard de Strasbourg',
              city: 'AULNAY SOUS BOIS',
              dateCreated: '2018-09-21T09:15:22.470675Z',
              dateModifiedAtLastProvider: '2018-02-01T14:47:00Z',
              dehumanizedId: 1,
              dehumanizedLastProviderId: 7,
              firstThumbDominantColor: null,
              id: 'AE',
              idAtProviders: '2949',
              isActive: true,
              lastProviderId: 'A4',
              modelName: 'Offerer',
              name: "Folies d'encre Aulnay-sous-Bois",
              postalCode: '93600',
              siren: '302559178',
              thumbCount: 0,
            },
            managingOffererId: 'AE',
            modelName: 'Venue',
            name: "Folies d'encre Aulnay-sous-Bois",
            postalCode: '93600',
            siret: '30255917864062',
            thumbCount: 0,
          },
          venueId: 'AE',
        },
        offerId: 'Q4',
        search: 'conspiration',
        shareMedium: null,
        userId: 'AE',
        validUntilDate: '2018-09-22T10:06:06.837449Z',
      },
    ]

    describe('with navigation by offer types mode', () => {
      describe('when there is items', () => {
        it('should not render title', () => {
          // given
          props.items = items

          // when
          const wrapper = shallow(<SearchResults {...props} />)
          const resultsTitle = wrapper.is('h2')
          const SearchResultItemWrapper = wrapper.find(SearchResultItem)
          const item = {
            recommendation: items[0],
          }

          // then
          expect(resultsTitle).toBe(false)
          expect(SearchResultItemWrapper.props()).toEqual(item)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // when
          const wrapper = shallow(<SearchResults {...props} />)
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(SearchResultItem)

          // then
          expect(resultsTitle.children).toEqual(
            "Il n'y a pas d'offres dans cette catégorie pour le moment."
          )
          expect(SearchResultItemWrapper.length).toEqual(0)
        })
      })
    })

    describe('without navigation by offer types mode', () => {
      describe('when there is a result with only key words', () => {
        it('should render properly the result title and item', () => {
          // given
          props.cameFromOfferTypesPage = false
          props.items = items

          // when
          const wrapper = shallow(<SearchResults {...props} />)
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(SearchResultItem)
          const item = {
            recommendation: items[0],
          }

          // then
          expect(resultsTitle.children).toEqual('"fakeKeywords" : 1 résultat')
          expect(SearchResultItemWrapper.props()).toEqual(item)
        })
      })

      describe('when there is no result', () => {
        it('should render properly the result title with no item', () => {
          // given
          props.cameFromOfferTypesPage = false

          // when
          const wrapper = shallow(<SearchResults {...props} />)
          wrapper.setState({ hasReceivedFirstSuccessData: true })
          const resultsTitle = wrapper.find('h2').props()
          const SearchResultItemWrapper = wrapper.find(SearchResultItem)

          // then
          expect(resultsTitle.children).toEqual('"fakeKeywords" : 0 résultat')
          expect(SearchResultItemWrapper.length).toEqual(0)
        })
      })
    })
  })
})
