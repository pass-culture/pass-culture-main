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
    it('enable to select only digital venues', () => {
      // when
      const props = mapDispatchToProps()

      // then
      expect(props).toHaveProperty('selectOnlyDigitalVenues')
    })

    it('preserve venue filter when select only digital venues', () => {
      // given
      const dispatch = jest.fn()
      const props = mapDispatchToProps(dispatch)

      //when
      props.selectOnlyDigitalVenues(true)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })
    })

    it('preserve venue filter when select only digital venues', () => {
      // given
      const dispatch = jest.fn()
      const props = mapDispatchToProps(dispatch)

      //when
      props.selectOnlyDigitalVenues(false)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })
    })

    it('enable to filter on a specific venue', () => {
      // when
      const props = mapDispatchToProps()

      // then
      expect(props).toHaveProperty('selectBookingsForVenues')
    })

    it('preserve selected venue', () => {
      // given
      const dispatch = jest.fn()
      const props = mapDispatchToProps(dispatch)

      //when
      props.selectBookingsForVenues('AVJA')

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: 'AVJA',
        type: 'BOOKING_SUMMARY_SELECT_VENUE',
      })
    })
  })
})
