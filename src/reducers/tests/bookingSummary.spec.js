import bookingSummary from '../bookingSummary'

describe('src | reducers | bookingSummary', () => {
  it('should return initial state', () => {
    // when
    const nextState = bookingSummary()

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues: false,
      selectedVenue: '',
    })
  })

  it('should update selectedVenue when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues: false,
      selectedVenue: '',
    }
    const action = {
      payload: 'A8KQ',
      type: 'BOOKING_SUMMARY_SELECT_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues: false,
      selectedVenue: 'A8KQ',
    })
  })

  it('should reinitialize selectedOffer when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues: false,
      selectedVenue: 'AGAQ',
    }
    const action = {
      payload: 'A8KQ',
      type: 'BOOKING_SUMMARY_SELECT_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues: false,
      selectedVenue: 'A8KQ',
    })
  })

  describe('BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE', () => {
    it('should reinitialize selectedVenue when filtering on digital venues', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'A8KQ',
      }

      // when
      const nextState = bookingSummary(initialState, {
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })

      // then
      expect(nextState).toEqual({
        isFilterByDigitalVenues: true,
        selectedVenue: '',
      })
    })

    it('should change state when not filtering on digital venues anymore', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: true,
        selectedVenue: '',
      }

      // when
      const nextState = bookingSummary(initialState, {
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      })

      // then
      expect(nextState).toEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: '',
      })
    })

    it('should reset selected venue when filtering on digital venues', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
      }
      const action = {
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toEqual({
        isFilterByDigitalVenues: true,
        selectedVenue: '',
      })
    })
  });
})
