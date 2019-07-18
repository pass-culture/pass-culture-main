import { mapStateToProps, mapDispatchToProps } from '../FilterByDateContainer'

describe('src | components | pages | Bookings | FilterByDateContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props that keep the state information : selected date', () => {
      // given
      const state = {
        bookingSummary: {
          selectBookingsDateFrom: new Date(2018, 1, 1),
          selectBookingsDateTo: new Date(2018, 1, 1),
        },
        data: {
          offers: [],
          stocks: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toMatchObject({
        selectBookingsDateFrom: new Date(2018, 1, 1),
        selectBookingsDateTo: new Date(2018, 1, 1),
      })
    })

    describe('showDateSection', () => {
      it('should not display date section by default', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectedVenue: '',
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
        expect(props).toHaveProperty('showThingDateSection', false)
      })

      it('should display a date periode selector when an offer of type thing is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: 'CY',
            selectedVenue: '',
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
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showEventDateSection', false)
        expect(props).toHaveProperty('showThingDateSection', true)
      })

      it('should display event dates selector when an offer of type event is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: 'DA',
            selectedVenue: '',
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
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showEventDateSection', true)
        expect(props).toHaveProperty('showThingDateSection', false)
      })

      it('should not display date section when `all offers` is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: 'all',
            selectedVenue: 'VU',
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
        expect(props).toHaveProperty('showThingDateSection', false)
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

    it('preserve selected date from', () => {
      // given
      const selectedDate = new Date(2018, 1, 1)
      //when
      props.selectBookingsDateFrom(selectedDate)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: selectedDate,
        type: 'BOOKING_SUMMARY_SELECT_DATE_FROM',
      })
    })

    it('preserve selected date to', () => {
      // given
      const selectedDate = new Date(2018, 1, 1)
      //when
      props.selectBookingsDateTo(selectedDate)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: selectedDate,
        type: 'BOOKING_SUMMARY_SELECT_DATE_TO',
      })
    })
  })
})
