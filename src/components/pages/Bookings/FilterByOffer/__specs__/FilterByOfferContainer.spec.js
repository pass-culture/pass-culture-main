import { mapStateToProps, mapDispatchToProps } from '../FilterByOfferContainer'

describe('src | components | pages | Bookings | FilterByOfferContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props that keep the state information : filter by offer', () => {
      // given
      const state = {
        bookingSummary: {
          isFilterByDigitalVenues: false,
          selectedVenue: 'CY',
        },
        data: {
          offers: [],
          venues: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toMatchObject({
        isFilterByDigitalVenues: false,
        offersOptions: [
          {
            id: 'all',
            name: 'Toutes les offres',
          },
        ],
        selectedVenue: 'CY',
      })
    })

    describe('showDateSection', () => {
      it('should be hidden by default', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', false)
      })

      it('should be displayed when a specific offer is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: 'CY',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', true)
      })

      it('should be hidden when `all offers is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: 'all',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showDateSection', false)
      })
    })

    describe('offerOptions', () => {
      it('should return only digital offer when is filtered by digital venues', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedVenue: '',
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
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toMatchObject({
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
        })
      })

      it('should return only non digital offer when `all venues`are selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedVenue: 'all',
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
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toMatchObject({
          offersOptions: [
            {
              id: 'all',
              name: 'Toutes les offres',
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
        })
      })

      it('should return proper offers when is filtered by a specific venue', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedVenue: 'AB',
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
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toMatchObject({
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
        })
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch

    beforeEach(() => {
      dispatch = jest.fn()
    })

    it('ebnable to load offers', () => {
      //when
      mapDispatchToProps(dispatch).loadOffers()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: { apiPath: '/offers', method: 'GET', stateKey: 'offers' },
        type: 'REQUEST_DATA_GET_OFFERS',
      })
    })

    it('preserve selected offer', () => {
      // when
      mapDispatchToProps(dispatch).selectBookingsForOffers({ target: { value: 'AVJA' } })

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: 'AVJA',
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      })
    })
  })
})
