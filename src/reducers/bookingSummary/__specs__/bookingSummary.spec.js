import bookingSummary from '../bookingSummary'

describe('src | reducers | bookingSummary', () => {
  it('should return initial state', () => {
    // when
    const nextState = bookingSummary()

    // then
    expect(nextState).toStrictEqual({
      isFilterByDigitalVenues: false,
      selectedVenue: '',
      selectedOffer: '',
      selectOffersFrom: '',
      selectOffersTo: '',
    })
  })

  describe('bOOKING_SUMMARY_SELECT_VENUE', () => {
    it('should change state when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: '',
        selectedOffer: '',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_SELECT_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'A8KQ',
        selectedOffer: '',
      })
    })

    it('should reinitialize selectedVenue when action BOOKING_SUMMARY_SELECT_VENUE occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'AGAQ',
        selectedOffer: '',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_SELECT_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'A8KQ',
        selectedOffer: '',
      })
    })

    it('should reinitialize selected offer when selecting another venue', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
        selectedOffer: 'A8KQ',
      }
      const action = {
        payload: 'AD4',
        type: 'BOOKING_SUMMARY_SELECT_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'AD4',
        selectedOffer: '',
      })
    })

    it('should reinitialize selected offer and dates when selecting `all venues` option', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
        selectedOffer: 'A8KQ',
        selectOffersFrom: new Date(2018, 1, 1),
        selectOffersTo: new Date(2018, 1, 31),
      }
      const action = {
        payload: 'all',
        type: 'BOOKING_SUMMARY_SELECT_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'all',
        selectedOffer: '',
        selectOffersFrom: '',
        selectOffersTo: '',
      })
    })
  })

  describe('bOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE', () => {
    it('should reinitialize selected offer and venue when filtering on digital venues', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
        selectedOffer: 'A8KQ',
      }
      const action = {
        payload: true,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: true,
        selectedVenue: '',
        selectedOffer: '',
      })
    })

    it('should change state when not filtering on digital venues anymore', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: true,
        selectedVenue: '',
        selectedOffer: '',
      }
      const action = {
        payload: false,
        type: 'BOOKING_SUMMARY_IS_FILTERED_BY_DIGITAL_VENUE',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: '',
        selectedOffer: '',
      })
    })
  })

  describe('bOOKING_SUMMARY_SELECT_OFFER', () => {
    it('should change state when action BOOKING_SUMMARY_SELECT_OFFER occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: '',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
      })
    })

    it('should reinitialize selectedOffer when action BOOKING_SUMMARY_SELECT_OFFER occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'AGAQ',
      }
      const action = {
        payload: 'A8KQ',
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
      })
    })

    it('should reinitialize selected dates when selecting `all offers` option', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
        selectedOffer: 'A8KQ',
        selectOffersFrom: new Date(2018, 1, 1),
        selectOffersTo: new Date(2018, 1, 31),
      }
      const action = {
        payload: 'all',
        type: 'BOOKING_SUMMARY_SELECT_OFFER',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'VYZU',
        selectedOffer: 'all',
        selectOffersFrom: '',
        selectOffersTo: '',
      })
    })
  })

  describe('bOOKING_SUMMARY_SELECT_DATE_FROM', () => {
    it('should change state when action bOOKING_SUMMARY_SELECT_DATE_FROM occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
        selectOffersFrom: new Date(2018, 1, 1),
        selectOffersTo: new Date(2018, 1, 31),
      }
      const date = new Date(2019, 6, 1)
      const action = {
        payload: date,
        type: 'BOOKING_SUMMARY_SELECT_DATE_FROM',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      const expectedDate = new Date(2019, 6, 1)
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
        selectOffersFrom: expectedDate,
        selectOffersTo: new Date(2018, 1, 31),
      })
    })
  })

  describe('bOOKING_SUMMARY_SELECT_DATE_TO', () => {
    it('should change state when action bOOKING_SUMMARY_SELECT_DATE_TO occured', () => {
      // given
      const initialState = {
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
        selectOffersFrom: new Date(2018, 1, 1),
        selectOffersTo: new Date(2018, 1, 31),
      }
      const date = new Date(2019, 6, 1)
      const action = {
        payload: date,
        type: 'BOOKING_SUMMARY_SELECT_DATE_TO',
      }

      // when
      const nextState = bookingSummary(initialState, action)

      // then
      const expectedDate = new Date(2019, 6, 1)
      expect(nextState).toStrictEqual({
        isFilterByDigitalVenues: false,
        selectedVenue: 'CY',
        selectedOffer: 'A8KQ',
        selectOffersFrom: new Date(2018, 1, 1),
        selectOffersTo: expectedDate,
      })
    })
  })
})
