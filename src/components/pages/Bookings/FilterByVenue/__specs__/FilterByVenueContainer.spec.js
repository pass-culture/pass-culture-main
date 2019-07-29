import { mapStateToProps, mapDispatchToProps } from '../FilterByVenueContainer'

describe('src | components | pages | Bookings | FilterByVenueContainer', () => {
  describe('mapStateToProps', () => {
    it('should return an object of props', () => {
      // given
      const state = {
        bookingSummary: {
          isFilteredByDigitalVenues: false,
          venueId: 'AYJA',
        },
        data: {
          offers: [],
          venues: [],
        },
      }

      // when
      const props = mapStateToProps(state)

      // then
      expect(props).toStrictEqual({
        isDigital: false,
        venueId: 'AYJA',
        venuesOptions: [
          {
            id: 'all',
            name: 'Tous les lieux',
          },
        ],
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

    it('should load venues using API', () => {
      //when
      props.loadVenues()

      // then
      expect(dispatch).toHaveBeenCalledWith({
        config: { apiPath: '/venues', method: 'GET', stateKey: 'venues' },
        type: 'REQUEST_DATA_GET_VENUES',
      })
    })

    it('should update isFilteredByDigitalVenues value from store to true', () => {
      //when
      props.updateIsFilteredByDigitalVenues(true)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES',
      })
    })

    it('should update isFilteredByDigitalVenues value from store to false', () => {
      //when
      props.updateIsFilteredByDigitalVenues(false)

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES',
      })
    })

    it('should update venueId value from store to given value', () => {
      //when
      props.updateVenueId({ target: { value: 'AVJA' } })

      // then
      expect(dispatch).toHaveBeenCalledWith({
        payload: 'AVJA',
        type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
      })
    })
  })
})
