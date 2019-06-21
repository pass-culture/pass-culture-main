import bookingSummary from '../bookingSummary'

describe('src | reducers | bookingSummary', () => {
  it('should return initial state', () => {
    // when
    const nextState = bookingSummary()

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:false,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    })
  })

  it('should update isFilterByDigitalVenues when action BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:false,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    }
    const action = {
      payload: true,
      type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:true,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    })
  })

  it('should update selectedVenue when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:false,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    }
    const action = {
      payload: 'A8KQ',
      type: 'BOOKING_SUMMARY_SELECT_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:false,
      selectedVenue:'A8KQ',
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    })
  })

  it('should reinitialize selectedOffer when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:false,
      selectedVenue:'AGAQ',
      selectedOffer:'AFAQ',
      selectOffersSince:new Date(2018, 1, 1),
    }
    const action = {
      payload: 'A8KQ',
      type: 'BOOKING_SUMMARY_SELECT_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:false,
      selectedVenue:'A8KQ',
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    })
  })


  it('should reinitialize selectedVenue and selectedOffer when action BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:false,
      selectedVenue:'A8KQ',
      selectedOffer:'AFAQ',
      selectOffersSince:new Date(2018, 1, 1),
    }
    const action = {
      payload: true,
      type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:true,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    })
  })

  it('should update selectedOffer when action BOOKING_SUMMARY_SELECT_OFFER occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:true,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    }
    const action = {
      payload: 'AVJA',
      type: 'BOOKING_SUMMARY_SELECT_OFFER',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    expect(nextState).toEqual({
      isFilterByDigitalVenues:true,
      selectedVenue:"",
      selectedOffer:'AVJA',
      selectOffersSince:new Date(2018, 1, 1),
    })
  })

  it('should update selectOffersSince when action BOOKING_SUMMARY_SELECT_DATE occured', () => {
    // given
    const initialState = {
      isFilterByDigitalVenues:false,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:new Date(2018, 1, 1),
    }
    const date = new Date(2019, 6, 1)
    const action = {
      payload:date,
      type: 'BOOKING_SUMMARY_SELECT_DATE',
    }

    // when
    const nextState = bookingSummary(initialState, action)

    // then
    const expectedDate = new Date(2019, 6, 1)
    expect(nextState).toEqual({
      isFilterByDigitalVenues:false,
      selectedVenue:"",
      selectedOffer:"",
      selectOffersSince:expectedDate,
    })
  })
})
