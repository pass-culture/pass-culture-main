import { mapStateToProps, mapDispatchToProps } from '../FilterByVenueContainer'

describe('src | components | pages | Bookings | FilterByVenueContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props that keep the state information : filter on digital venues', () => {
      // given
      const state = {
        bookingSummary: {
          isFilterByDigitalVenues: true,
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
        isDigital: true,
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

    it('ebnable to load venues', () => {
      //when
      props.loadVenues()

      // then
      expect(dispatch).toHaveBeenCalledWith(
        {
          "config":
            {"apiPath": "/venues",
              "method": "GET",
              "stateKey": "venues",
            },
          "type": "REQUEST_DATA_GET_VENUES",
        }
    )
    })

    it('preserve venue filter when select only digital venues', () => {
      //when
      props.selectOnlyDigitalVenues(true)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })
    })

    it('preserve venue filter when select only digital venues', () => {
      //when
      props.selectOnlyDigitalVenues(false)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })
    })

    it('preserve selected venue', () => {
        //when
        props.selectBookingsForVenues({target:{value:'AVJA'}})

        // then
        expect(dispatch).toHaveBeenCalledWith({
          payload: 'AVJA',
          type: 'BOOKING_SUMMARY_SELECT_VENUE',
        })
    })
  })
})
