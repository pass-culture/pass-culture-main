import { humanizeBeginningDateTime, mapStateToProps, mergeProps } from '../TeaserContainer'

jest.spyOn(Date, 'now').mockImplementation(() => '2002-07-21T20:00:00Z')

describe('src | components | layout | Teaser | TeaserContainer', () => {
  let ownProps
  let state

  beforeEach(() => {
    ownProps = {
      handleToggleTeaser: jest.fn(),
      favorite: {
        offerId: 'o1',
        thumbUrl: 'fake/thumb/url',
      },
      isEditMode: false,
      match: {
        path: '/fake-url',
      },
    }
    state = {
      data: {
        bookings: [
          {
            id: 'b1',
            stockId: 's1',
          },
        ],
        offers: [
          {
            dateRange: ['2000-07-21T20:00:00Z', '2030-08-21T20:00:00Z'],
            id: 'o1',
            isActive: true,
            hasBookingLimitDatetimesPassed: false,
            name: 'Fake offer name',
            subcategoryId: 'cinema',
            venue: {
              latitude: 48.91683,
              longitude: 2.4388,
            },
          },
        ],
        stocks: [
          {
            id: 's1',
            beginningDatetime: '2002-07-21T21:00:00Z',
            offerId: 'o1',
          },
        ],
        categories: [
          {
            subcategories: [{ id: 'cinema', searchGroupName: 'CINEMA' }],
            searchGroups: [
              { name: 'LIVRE', value: 'Livre' },
              { name: 'CINEMA', value: 'Cinéma' },
            ],
          },
        ],
      },
      geolocation: {
        latitude: 48.8636537,
        longitude: 2.3371206000000004,
      },
    }
  })

  describe('humanizeBeginningDateTime()', () => {
    describe('when has no bookings', () => {
      it('should return an empty string', () => {
        // given
        const hasBookings = false
        const booking = {}

        // when
        const result = humanizeBeginningDateTime(hasBookings, state, booking)

        // then
        expect(result).toBe('')
      })
    })

    describe('when has bookings', () => {
      it('should return a humanize relative date', () => {
        // given
        const hasBookings = true
        const booking = state.data.bookings[0]

        // when
        const result = humanizeBeginningDateTime(hasBookings, state, booking)

        // then
        expect(result).toBe('Aujourd’hui')
      })
    })
  })

  describe('mapStateToProps()', () => {
    describe('when have bookings', () => {
      it('should return props', () => {
        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          date: 'du 21/07/2000 au 21/08/2030',
          detailsUrl: '/fake-url/details/o1/vide',
          handleToggleTeaser: expect.any(Function),
          humanizeRelativeDistance: '10 km',
          isEditMode: false,
          name: 'Fake offer name',
          offerId: 'o1',
          searchGroupLabel: 'Cinéma',
          statuses: [
            { class: 'booked', label: 'Réservé' },
            {
              class: 'today',
              label: 'Aujourd’hui',
            },
          ],
          thumbUrl: 'fake/thumb/url',
        })
      })
    })

    describe('when no bookings', () => {
      it('should return props', () => {
        // given
        state.data.bookings = []

        // when
        const props = mapStateToProps(state, ownProps)

        // then
        expect(props).toStrictEqual({
          date: 'du 21/07/2000 au 21/08/2030',
          detailsUrl: '/fake-url/details/o1/vide',
          handleToggleTeaser: expect.any(Function),
          humanizeRelativeDistance: '10 km',
          isEditMode: false,
          name: 'Fake offer name',
          offerId: 'o1',
          searchGroupLabel: 'Cinéma',
          statuses: [],
          thumbUrl: 'fake/thumb/url',
        })
      })
    })
  })

  describe('mergeProps', () => {
    it('should map trackConsultOffer using trackEvent from props', () => {
      const stateProps = {
        offerId: 'B4',
      }
      const ownProps = {
        tracking: {
          trackEvent: jest.fn(),
        },
      }
      mergeProps(stateProps, {}, ownProps).trackConsultOffer()
      expect(ownProps.tracking.trackEvent).toHaveBeenCalledWith({
        action: 'ConsultOffer_FromFavorite',
        name: 'B4',
      })
    })

    it('should spread props from stateProps', () => {
      const stateProps = {
        offerId: 'B4',
      }
      const result = mergeProps(stateProps, {}, {})
      expect(result.offerId).toBe('B4')
    })
  })
})
