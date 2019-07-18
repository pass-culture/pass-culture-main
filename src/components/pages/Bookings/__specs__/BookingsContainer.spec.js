import { mapStateToProps } from '../BookingsContainer'

describe('src | components | pages | Bookings | BookingsContainer', () => {
  describe('mapStateToProps', () => {
    describe('pathToCsvFile', () => {
      describe('when a venue and offer is selected', () => {
        it('should limit csv to this venue and this offer and this date', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedOffer: 'CY',
              selectOffersFrom: new Date('2019-07-17T14:35:31.000Z').toISOString(),
              selectOffersTo: new Date('2019-07-17T14:35:31.000Z').toISOString(),
              selectedVenue: 'F51',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile:
              'http://localhost/bookings/csv?venueId=F51&offerId=CY&dateFrom=2019-07-17T14:35:31.000Z&dateTo=2019-07-17T14:35:31.000Z',
            showButtons: true,
            showOfferSection: true,
          })
        })

        it("should target the API without filter on venueId when 'all venues' option is selected", () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedOffer: '',
              selectOffersFrom: '',
              selectOffersTo: '',
              selectedVenue: 'all',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv',
            showButtons: true,
            showOfferSection: false,
          })
        })

        it("should target the API without filter on offerId when 'all offers' option is selected", () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: false,
              selectedOffer: 'all',
              selectOffersFrom: '',
              selectOffersTo: '',
              selectedVenue: 'F51',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile: 'http://localhost/bookings/csv?venueId=F51',
            showButtons: true,
            showOfferSection: true,
          })
        })
      })

      describe('when filtering on digital venue and offerId', () => {
        it('should limit csv to these digital venues, offer and date', () => {
          // given
          const state = {
            bookingSummary: {
              isFilterByDigitalVenues: true,
              selectedOffer: 'AR',
              selectOffersFrom: '2019-07-17T14:35:31.702139Z',
              selectOffersTo: '2019-07-17T14:35:31.702139Z',
              selectedVenue: '',
            },
          }

          // when
          const props = mapStateToProps(state)

          // then
          expect(props).toStrictEqual({
            pathToCsvFile:
              'http://localhost/bookings/csv?onlyDigitalVenues=true&offerId=AR&dateFrom=2019-07-17T14:35:31.702139Z&dateTo=2019-07-17T14:35:31.702139Z',
            showButtons: true,
            showOfferSection: true,
          })
        })
      })
    })

    describe('showButtons', () => {
      it('should be displayed when downloading digital venues and an offer is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: 'A4',
            selectOffersFrom: '',
            selectOffersTo: '',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: 'http://localhost/bookings/csv?onlyDigitalVenues=true&offerId=A4',
          showButtons: true,
          showOfferSection: true,
        })
      })

      it('should be displayed when a venue and an offer is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: 'CY',
            selectOffersFrom: '',
            selectOffersTo: '',
            selectedVenue: 'G2YU',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: 'http://localhost/bookings/csv?venueId=G2YU&offerId=CY',
          showButtons: true,
          showOfferSection: true,
        })
      })

      it('should not be displayed when a specific venue is selected and no offer is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectOffersFrom: '',
            selectOffersTo: '',
            selectedVenue: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: 'http://localhost/bookings/csv?venueId=CY',
          showButtons: false,
          showOfferSection: true,
        })
      })

      it('should be displayed when the `all venues` options are selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectOffersFrom: '',
            selectOffersTo: '',
            selectedVenue: 'all',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toStrictEqual({
          pathToCsvFile: 'http://localhost/bookings/csv',
          showButtons: true,
          showOfferSection: false,
        })
      })
    })

    describe('showOfferSection', () => {
      it('should not be displayed by default', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', false)
      })

      it('should be displayed when a venue is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: false,
            selectedOffer: '',
            selectedVenue: 'CY',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', true)
      })

      it('should be displayed when digital venues are selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: '',
            selectedVenue: '',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', true)
      })

      it('should not be displayed when `all venues` is selected', () => {
        // given
        const state = {
          bookingSummary: {
            isFilterByDigitalVenues: true,
            selectedOffer: '',
            selectedVenue: 'all',
          },
        }

        // when
        const props = mapStateToProps(state)

        // then
        expect(props).toHaveProperty('showOfferSection', false)
      })
    })
  })
})
