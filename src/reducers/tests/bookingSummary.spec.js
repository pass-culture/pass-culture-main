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

  it('should update isFilterByDigitalVenues when action BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues: false,
      selectedVenue: '',
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

  it('should reinitialize selectedVenue and selectedOffer when action BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues: false,
      selectedVenue: 'A8KQ',
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
})
