import bookingSummary from '../bookingSummary'

describe('src | reducers | bookingSummary', () => {
  it('should return initial state', () => {
    // when
    const nextState = bookingSummary()

    // then
    expect(nextState).toStrictEqual({
      bookingsFrom: '',
      bookingsTo: '',
      isFilteredByDigitalVenues: false,
      offerId: '',
      venueId: '',
    })
  })

  describe('when BOOKING_SUMMARY_UPDATE_VENUE_ID', () => {
    it('should change state when action BOOKING_SUMMARY_UPDATE_VENUE_ID occurred', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: '',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'A8KQ',
      })
    })

    it('should reinitialize venueId when action BOOKING_SUMMARY_UPDATE_VENUE_ID occurred', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'AGAQ',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'A8KQ',
      })
    })

    it('should reinitialize selected offer when selecting another venue', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'VYZU',
      }
      const action = {
        payload: 'AD4',
        type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'AD4',
      })
    })

    it('should reinitialize selected offer and dates when selecting `all venues` option', () => {
      // given
      const initialState = {
        bookingsFrom: new Date(2018, 1, 1),
        bookingsTo: new Date(2018, 1, 31),
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'VYZU',
      }
      const action = {
        payload: 'all',
        type: 'BOOKING_SUMMARY_UPDATE_VENUE_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'all',
      })
    })
  })

  describe('when BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES', () => {
    it('should reinitialize bookingFrom, bookingTo, offerId and venueId when filtering on digital venues', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'VYZU',
      }
      const action = {
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: true,
        offerId: '',
        venueId: '',
      })
    })

    it('should change state when not filtering on digital venues anymore', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: true,
        offerId: '',
        venueId: '',
      }
      const action = {
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUES',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: '',
      })
    })
  })

  describe('when BOOKING_SUMMARY_UPDATE_OFFER_ID', () => {
    it('should change state when action BOOKING_SUMMARY_UPDATE_OFFER_ID occurred', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: '',
        venueId: 'CY',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_UPDATE_OFFER_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      })
    })

    it('should reinitialize offerId when action BOOKING_SUMMARY_UPDATE_OFFER_ID occurred', () => {
      // given
      const initialState = {
        isFilteredByDigitalVenues: false,
        offerId: 'AGAQ',
        venueId: 'CY',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_UPDATE_OFFER_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      })
    })

    it('should reinitialize selected dates when selecting `all offers` option', () => {
      // given
      const initialState = {
        bookingsFrom: new Date(2018, 1, 1),
        bookingsTo: new Date(2018, 1, 31),
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'VYZU',
      }
      const action = {
        payload: 'all',
        type: 'BOOKING_SUMMARY_UPDATE_OFFER_ID',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        bookingsFrom: '',
        bookingsTo: '',
        isFilteredByDigitalVenues: false,
        offerId: 'all',
        venueId: 'VYZU',
      })
    })
  })

  describe('when BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM', () => {
    it('should change state when action BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM occurred', () => {
      // given
      const initialState = {
        bookingsFrom: new Date(2018, 1, 1),
        bookingsTo: new Date(2018, 1, 31),
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      }
      const date = new Date(2019, 6, 1)
      const action = {
        payload: date,
        type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_FROM',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      const expectedDate = new Date(2019, 6, 1)
      expect(nextState).toStrictEqual({
        bookingsFrom: expectedDate,
        bookingsTo: new Date(2018, 1, 31),
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      })
    })
  })

  describe('when BOOKING_SUMMARY_UPDATE_BOOKINGS_TO', () => {
    it('should change state when action BOOKING_SUMMARY_UPDATE_BOOKINGS_TO occurred', () => {
      // given
      const initialState = {
        bookingsFrom: new Date(2018, 1, 1),
        bookingsTo: new Date(2018, 1, 31),
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      }
      const date = new Date(2019, 6, 1)
      const action = {
        payload: date,
        type: 'BOOKING_SUMMARY_UPDATE_BOOKINGS_TO',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      const expectedDate = new Date(2019, 6, 1)
      expect(nextState).toStrictEqual({
        bookingsFrom: new Date(2018, 1, 1),
        bookingsTo: expectedDate,
        isFilteredByDigitalVenues: false,
        offerId: 'A8KQ',
        venueId: 'CY',
      })
    })
  })
})
