import { mapStateToProps, mapDispatchToProps } from '../FilterByOfferContainer'

describe('src | components | pages | Bookings | FilterByOfferContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        bookingSummary: {
          isFilteredByDigitalVenues: false,
          offerId: '',
          venueId: 'CY',
        },
        data: {
          offers: [],
          venues: [],
          users: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isFilteredByDigitalVenues: false,
        offersOptions: [
          {
            id: 'all',
            name: 'Toutes les offres',
          },
        ],
        offerId: '',
        venueId: 'CY',
        showDateSection: false,
      })
    })

    it('should return an empty list of offers options when user is admin', () => {
      // given
      const state = {
        bookingSummary: {
          isFilteredByDigitalVenues: false,
          offerId: '',
          venueId: '',
        },
        data: {
          offers: [],
          users: [
            {
              id: 'EY',
              isAdmin: 'True',
            },
          ],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isFilteredByDigitalVenues: false,
        offerId: '',
        offersOptions: [],
        showDateSection: false,
        venueId: '',
      })
    })

    describe('showDateSection', () => {
      it('should be false by default', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: '',
          },
          data: {
            offers: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', false)
      })

      it('should be true when a specific offer is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: 'CY',
            venueId: '',
          },
          data: {
            offers: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', true)
      })

      it('should be false when offerId is `all`', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: 'all',
            venueId: '',
          },
          data: {
            offers: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', false)
      })

      it('should be false when offerId is null', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: null,
            venueId: '',
          },
          data: {
            offers: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', false)
      })
    })

    describe('offerOptions', () => {
      it('should return an array of digital offers when isFilteredByDigitalVenues is true', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: '',
            venueId: '',
          },
          data: {
            offers: [
              {
                id: 'CY',
                name: 'abonnement streaming',
                isDigital: true,
              },
              {
                id: 'DA',
                name: 'livre en librairie',
                isDigital: false,
              },
            ],
            venues: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          isFilteredByDigitalVenues: true,
          offersOptions: [
            {
              id: 'all',
              name: 'Toutes les offres',
            },
            {
              id: 'CY',
              name: 'abonnement streaming',
              isDigital: true,
            },
          ],
          offerId: '',
          venueId: '',
          showDateSection: false,
        })
      })

      it('should return an empty array when venueId is `all`', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'all',
          },
          data: {
            offers: [
              {
                id: 'CY',
                name: 'abonnement streaming',
                isDigital: true,
              },
              {
                id: 'DA',
                name: 'livre en librairie',
                isDigital: false,
              },
              {
                id: 'BA',
                name: 'place de cinéma',
                isDigital: false,
              },
            ],
            venues: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          isFilteredByDigitalVenues: false,
          offersOptions: [],
          offerId: '',
          venueId: 'all',
          showDateSection: false,
        })
      })

      it('should return an array of physical offers related to the given venueId ', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: false,
            offerId: '',
            venueId: 'AB',
          },
          data: {
            offers: [
              {
                id: 'CY',
                name: 'abonnement streaming',
                venueId: 'AB',
              },
              {
                id: 'DA',
                name: 'livre en librairie',
                venueId: 'CD',
              },
            ],
            venues: [],
            users: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          isFilteredByDigitalVenues: false,
          offersOptions: [
            {
              id: 'all',
              name: 'Toutes les offres',
            },
            {
              id: 'CY',
              name: 'abonnement streaming',
              venueId: 'AB',
            },
          ],
          offerId: '',
          venueId: 'AB',
          showDateSection: false,
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    describe('loadOffers from API', () => {
      it('should get all 1000 offers for offerer with all venues', () => {
        // given
        const { loadOffers } = mapDispatchToProps(dispatch)
        const venueId = 'all'

        // when
        loadOffers(venueId)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offers?paginate=1000',
            method: 'GET',
            normalizer: {
              mediations: 'mediations',
              product: {
                normalizer: { offers: 'offers' },
                stateKey: 'products',
              },
              stocks: 'stocks',
              venue: {
                normalizer: {
                  managingOfferer: 'offerers',
                },
                stateKey: 'venues',
              },
            },
            stateKey: 'offers',
          },
          type: 'REQUEST_DATA_GET_OFFERS',
        })
      })

      it('should get all 1000 offers for specific venue', () => {
        // given
        const { loadOffers } = mapDispatchToProps(dispatch)
        const venueId = 'AE'

        // when
        loadOffers(venueId)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: '/offers?paginate=1000&venueId=AE',
            method: 'GET',
            normalizer: {
              mediations: 'mediations',
              product: {
                normalizer: { offers: 'offers' },
                stateKey: 'products',
              },
              stocks: 'stocks',
              venue: {
                normalizer: {
                  managingOfferer: 'offerers',
                },
                stateKey: 'venues',
              },
            },
            stateKey: 'offers',
          },
          type: 'REQUEST_DATA_GET_OFFERS',
        })
      })
    })

    describe('updateOfferId', () => {
      it('should update offerId from store', () => {
        // given
        const functions = mapDispatchToProps(dispatch)
        const { updateOfferId } = functions

        // when
        updateOfferId({ target: { value: 'AVJA' } })

        // then
        expect(dispatch).toHaveBeenCalledWith({
          payload: 'AVJA',
          type: 'BOOKING_SUMMARY_UPDATE_OFFER_ID',
        })
      })
    })
  })
})
