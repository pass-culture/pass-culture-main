import { mapStateToProps, mapDispatchToProps } from '../FilterByDateContainer'

describe('src | components | pages | Bookings | FilterByDateContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        bookingSummary: {
          bookingsFrom: new Date(2018, 1, 1),
          bookingsTo: new Date(2018, 1, 1),
        },
        data: {
          offers: [],
          stocks: [],
          venues: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        showEventDateSection: false,
        showThingDateSection: false,
        stocks: [],
        timezone: 'Europe/Paris',
      })
    })

    describe('showEventDateSection', () => {
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
            stocks: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showEventDateSection', false)
      })

      it('should be true when an offer of type event is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'DA',
            venueId: 'BA',
          },
          data: {
            offers: [
              {
                id: 'DA',
                isThing: false,
                isEvent: true,
              },
              {
                id: 'CY',
                isThing: true,
                isEvent: false,
              },
            ],
            stocks: [],
            venues: [
              {
                id: 'BA',
                departementCode: '92',
              },
            ],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showEventDateSection', true)
      })

      it('should be false when `all offers` is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'all',
            venueId: 'VU',
          },
          data: {
            offer: [],
            stocks: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showEventDateSection', false)
      })
    })

    describe('showThingDateSection', () => {
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
            stocks: [],
            venues: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showThingDateSection', false)
      })

      it('should be true when an offer of type event is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'DA',
            venueId: 'BA',
          },
          data: {
            offers: [
              {
                id: 'DA',
                isThing: false,
                isEvent: true,
              },
              {
                id: 'CY',
                isThing: true,
                isEvent: false,
              },
            ],
            stocks: [],
            venues: [
              {
                id: 'BA',
                departementCode: '75',
              },
            ],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showThingDateSection', false)
      })

      it('should be false when `all offers` is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'all',
            venueId: 'VU',
          },
          data: {
            offer: [],
            stocks: [],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showThingDateSection', false)
      })
    })

    describe('stocks', () => {
      it('should return an array of stocks when offer is event', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'DA',
            venueId: 'BA',
          },
          data: {
            venues: [
              {
                id: 'BA',
                departementCode: '75',
              },
            ],
            offers: [
              {
                id: 'DA',
                isThing: false,
                isEvent: true,
              },
            ],
            stocks: [
              {
                beginningDatetime: '2019-08-08T21:59:00Z',
                id: 'ZY',
                offerId: 'DA',
              },
            ],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('stocks', [
          {
            beginningDatetime: '2019-08-08T21:59:00Z',
            id: 'ZY',
            offerId: 'DA',
          },
        ])
      })

      it('should return an array of stocks and venue timezone when offer is event', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'DA',
            venueId: 'BA',
          },
          data: {
            venues: [
              {
                id: 'BA',
                departementCode: '97',
              },
            ],
            offers: [
              {
                id: 'DA',
                isThing: false,
                isEvent: true,
              },
            ],
            stocks: [
              {
                beginningDatetime: '2019-08-08T21:59:00Z',
                id: 'ZY',
                offerId: 'DA',
              },
            ],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          showEventDateSection: true,
          showThingDateSection: false,
          stocks: [
            {
              beginningDatetime: '2019-08-08T21:59:00Z',
              id: 'ZY',
              offerId: 'DA',
            },
          ],
          timezone: 'America/Cayenne',
        })
      })

      it('should return an empty array when offer is thing', () => {
        // given
        const state = {
          bookingSummary: {
            isFilteredByDigitalVenues: true,
            offerId: 'CY',
            venueId: '',
          },
          data: {
            offers: [
              {
                id: 'CY',
                isThing: true,
                isEvent: false,
              },
            ],
            stocks: [
              {
                beginningDatetime: null,
                id: 'ARQ',
                offerId: 'CY',
              },
            ],
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('stocks', [])
      })
    })
  })

  describe('mapDispatchToProps', () => {
    let dispatch
    let props

    beforeEach(() => {
      dispatch = jest.fn()
      props = mapDispatchToProps(dispatch)
    })

    describe('updateBookingsFrom', () => {
      it('should dispatch an action to update `bookingsFrom` value from store', () => {
        // given
        const selectedDate = new Date(2018, 1, 1)

        //when
        props.updateBookingsFrom(selectedDate)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          payload: selectedDate,
          type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM',
        })
      })
    })

    describe('updateBookingsTo', () => {
      it('should dispatch an action to update `bookingsTo` value from store', () => {
        // given
        const selectedDate = new Date(2018, 1, 1)

        //when
        props.updateBookingsTo(selectedDate)

        // then
        expect(dispatch).toHaveBeenCalledWith({
          payload: selectedDate,
          type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_TO',
        })
      })
    })
  })
})
